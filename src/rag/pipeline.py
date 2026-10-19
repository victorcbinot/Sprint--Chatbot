"""
Pipeline de resposta -- Sprint 04.

Ponto único de entrada usado pela interface (app/app.py): une as camadas de
segurança da Sprint 03 com o RAG.

Ordem de execução:
  1. pergunta vazia          -> pede para repetir
  2. moderation.py           -> bloqueia jailbreak / prompt injection do usuário
  3. scope_validator.py      -> bloqueia pedidos de aconselhamento jurídico,
                                financeiro ou de segurança elétrica
  4. retriever + prompt RAG  -> responde só com o contexto recuperado, citando
                                a fonte

Decisão de projeto: o validador de escopo da Sprint 03 usa uma lista de
palavras-chave e, para qualquer pergunta sem nenhuma delas, devolve "fora de
escopo". Isso funcionava com o contexto fixo da Sprint 03, mas com uma base de
conhecimento que cresce seria frágil: uma pergunta legítima como "Como
funciona o cancelamento automático da reserva?" não tem nenhuma palavra da
lista e seria bloqueada por engano. Por isso aqui só usamos o validador para
os três tipos de recusa sensível (jurídico, financeiro, segurança elétrica).
A recusa de perguntas fora do contexto fica a cargo do grounding do prompt
RAG (responder só com o contexto recuperado), que é avaliada nos casos
"fora_do_contexto" e "sem_resposta_na_base" de evals/rag_eval_set.json.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

PASTA_DESTE_ARQUIVO = Path(__file__).parent
PASTA_SRC = PASTA_DESTE_ARQUIVO.parent
for pasta in (PASTA_DESTE_ARQUIVO, PASTA_SRC):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

from guardrails.moderation import MENSAGEM_RECUSA_JAILBREAK, detectar_jailbreak
from guardrails.scope_validator import TipoRecusa, validar_escopo
from prompt_rag import construir_chain_rag, formatar_contexto_com_citacao, pagina_humana
from retriever import buscar_contexto

TIPOS_BLOQUEADOS_NO_CODIGO = {
    TipoRecusa.ACONSELHAMENTO_JURIDICO,
    TipoRecusa.ACONSELHAMENTO_FINANCEIRO,
    TipoRecusa.SEGURANCA_ELETRICA,
}

TAMANHO_TRECHO = 260


@dataclass
class Fonte:
    documento: str
    pagina: object
    trecho: str


@dataclass
class Resposta:
    texto: str
    fontes: list[Fonte] = field(default_factory=list)
    bloqueado: bool = False
    motivo: str | None = None


def verificar_seguranca(pergunta: str) -> Resposta | None:
    """Devolve uma Resposta de recusa se a pergunta deve ser bloqueada
    antes de chegar ao modelo; devolve None se pode seguir para o RAG."""
    moderacao = detectar_jailbreak(pergunta)
    if not moderacao.seguro:
        return Resposta(
            texto=MENSAGEM_RECUSA_JAILBREAK,
            bloqueado=True,
            motivo="tentativa de jailbreak / prompt injection",
        )

    escopo = validar_escopo(pergunta)
    if not escopo.dentro_do_escopo and escopo.tipo_recusa in TIPOS_BLOQUEADOS_NO_CODIGO:
        return Resposta(
            texto=escopo.mensagem,
            bloqueado=True,
            motivo=escopo.tipo_recusa.value,
        )
    return None


def responder_pergunta(pergunta: str, vector_store, llm, versao_prompt: str = "v1", k: int = 4) -> Resposta:
    pergunta = (pergunta or "").strip()
    if not pergunta:
        return Resposta(texto="Pode repetir a pergunta?", bloqueado=True, motivo="pergunta vazia")

    bloqueio = verificar_seguranca(pergunta)
    if bloqueio is not None:
        return bloqueio

    documentos = buscar_contexto(pergunta, vector_store, k=k)
    contexto = formatar_contexto_com_citacao(documentos)

    chain = construir_chain_rag(llm, versao_prompt=versao_prompt)
    texto = chain.invoke({"pergunta": pergunta, "contexto": contexto})

    fontes = []
    for doc in documentos:
        trecho = " ".join(doc.page_content.split())
        if len(trecho) > TAMANHO_TRECHO:
            trecho = trecho[:TAMANHO_TRECHO].rstrip() + "..."
        fontes.append(Fonte(
            documento=Path(doc.metadata.get("source", "desconhecido")).name,
            pagina=pagina_humana(doc),
            trecho=trecho,
        ))

    return Resposta(texto=texto, fontes=fontes)