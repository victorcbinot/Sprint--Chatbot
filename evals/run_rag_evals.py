"""
Roda o eval set do RAG (evals/rag_eval_set.json) e salva os resultados da
iteração em evals/rag_results_iter<N>.json.

Para cada caso:
  1. recupera o contexto (ou usa o contexto forçado, nos casos de injection)
  2. gera a resposta com a chain RAG (temperature 0)
  3. calcula as métricas determinísticas (contexto, citação, fatos, injection)
  4. pede ao LLM avaliador as notas de faithfulness e answer_relevancy
     (rubrica em evals/rubrica_rag.md, prompt em evals/judge_prompt_rag.md)

Requer: OLLAMA_API_KEY no .env (chat via Ollama Cloud), Ollama local com
nomic-embed-text, e o vector store já indexado
(python src/rag/indexar_base_de_conhecimento.py).

Uso:
    python evals/run_rag_evals.py --iteracao 1 --prompt v1 --k 4
    python evals/run_rag_evals.py --iteracao 2 --prompt v2 --k 4
    python evals/run_rag_evals.py --iteracao 1 --sem-juiz   # só métricas determinísticas
    python evals/run_rag_evals.py --iteracao 3 --prompt v1 --eval-set rag_eval_set_dificil.json
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PASTA_EVALS = Path(__file__).parent
RAIZ = PASTA_EVALS.parent
sys.path.insert(0, str(RAIZ / "src"))

from rag.prompt_rag import (
    construir_chain_rag,
    formatar_contexto_com_citacao,
)
from rag.retriever import buscar_contexto


# ---------------------------------------------------------------- utilidades

def carregar_eval_set(nome: str = "rag_eval_set.json") -> dict:
    return json.loads((PASTA_EVALS / nome).read_text(encoding="utf-8"))


def carregar_prompt_juiz() -> str:
    return (PASTA_EVALS / "judge_prompt_rag.md").read_text(encoding="utf-8")


def texto_da_resposta(resposta) -> str:
    """ChatOllama devolve mensagem (.content); modelos de teste podem devolver str."""
    return getattr(resposta, "content", resposta)


def nomes_das_fontes(documentos) -> list[str]:
    return [Path(d.metadata.get("source", "")).name for d in documentos]


# ------------------------------------------------------ métricas determinísticas

def normalizar(texto: str) -> str:
    """
    Normaliza o texto antes de comparar: o gpt-oss costuma escrever espaços e
    hífens "especiais" (U+202F, U+00A0, U+2011) que parecem iguais aos normais
    mas quebram a comparação de strings (ex.: "carregador 2" não era achado).
    Também remove caracteres invisíveis de formatação (zero-width space U+200B,
    BOM U+FEFF, soft hyphen U+00AD) que aparecem no meio de palavras -- ex.:
    "F{U+200B}onte:" não casava com a checagem de citação.
    Por fim, canoniza separadores de milhar: "5.000", "5 000" e "5000" passam a
    ser equivalentes (o modelo redesenha "R$ 5.000" como "5 000" com espaço
    fino, e a checagem de fatos era quebrada pela formatação).
    """
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"[\u2010-\u2015\u2212]", "-", texto)
    texto = re.sub(r"[\u200b-\u200f\u2060\ufeff\u00ad]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"(?<=\d)[.\s](?=\d{3}(?!\d))", "", texto)
    return texto.lower().strip()

def calcular_metricas_deterministicas(caso: dict, resposta: str, fontes_recuperadas: list[str]) -> dict:
    resposta_min = normalizar(resposta)
    esperadas = caso.get("fonte_esperada", [])
    fatos = caso.get("fatos_chave", [])
    deve_recusar = caso.get("deve_recusar", False)
    forcado = "contexto_forcado" in caso

    metricas = {}

    # qualidade da recuperação (não se aplica a contexto forçado nem a recusas)
    if esperadas and not forcado:
        metricas["context_hit"] = any(f in fontes_recuperadas for f in esperadas)

    if not deve_recusar:
        metricas["citation_present"] = "fonte:" in resposta_min
        if esperadas:
            metricas["fonte_correta"] = any(normalizar(f) in resposta_min for f in esperadas)
        if fatos:
            presentes = sum(1 for f in fatos if normalizar(f) in resposta_min)
            metricas["fact_recall"] = presentes / len(fatos)

    marcador = caso.get("marcador_proibido")
    if marcador:
        metricas["injection_resistido"] = normalizar(marcador) not in resposta_min

    return metricas


# ------------------------------------------------------------ avaliador (LLM)

def _extrair_json_do_juiz(bruto: str) -> dict:
    """Extrai o objeto JSON das notas, tolerando texto/código em volta e
    respostas truncadas (o modelo avaliador às vezes divaga antes do JSON)."""
    if not bruto:
        raise ValueError("resposta vazia do avaliador")

    candidatos = []
    for inicio in [i for i, c in enumerate(bruto) if c == "{"]:
        for fim in [i for i, c in enumerate(bruto) if c == "}" and i > inicio]:
            candidatos.append(bruto[inicio:fim + 1])

    for candidato in sorted(candidatos, key=len, reverse=True):
        try:
            dados = json.loads(candidato)
        except json.JSONDecodeError:
            continue
        if "faithfulness" in dados and "answer_relevancy" in dados:
            return dados

    raise ValueError("nenhum JSON válido com as notas foi encontrado")


def avaliar_com_juiz(llm_juiz, template_juiz: str, caso: dict, contexto: str, resposta: str) -> dict:
    prompt = (
        template_juiz
        .replace("<<PERGUNTA>>", caso["pergunta"])
        .replace("<<CONTEXTO>>", contexto)
        .replace("<<RESPOSTA>>", resposta)
        .replace("<<RESPOSTA_ESPERADA>>", caso["resposta_esperada"])
        .replace("<<DEVE_RECUSAR>>", "SIM" if caso.get("deve_recusar") else "NÃO")
    )

    ultimo_bruto = ""
    ultimo_erro = None
    # Duas tentativas: a segunda só acontece se o avaliador não devolver JSON
    # válido (resposta truncada/vazia), para não perder o caso.
    for tentativa in range(2):
        ultimo_bruto = texto_da_resposta(llm_juiz.invoke(prompt)) or ""
        try:
            dados = _extrair_json_do_juiz(ultimo_bruto)
            return {
                "faithfulness": float(dados["faithfulness"]),
                "answer_relevancy": float(dados["answer_relevancy"]),
                "recusou": bool(dados.get("recusou", False)),
                "justificativa": str(dados.get("justificativa", "")),
            }
        except Exception as erro:
            ultimo_erro = erro
            if tentativa == 0:
                prompt += (
                    "\n\nSua resposta anterior foi inválida ou truncada. Responda agora "
                    "SOMENTE com o objeto JSON completo, sem texto antes ou depois e sem "
                    "bloco de código."
                )

    return {"juiz_erro": f"{ultimo_erro}", "juiz_resposta_bruta": ultimo_bruto[:300]}


# ------------------------------------------------------------------- um caso

def avaliar_caso(caso, vector_store, chain_rag, llm_juiz, template_juiz, k, usar_juiz) -> dict:
    resultado = {
        "id": caso["id"],
        "categoria": caso["categoria"],
        "pergunta": caso["pergunta"],
    }
    try:
        if "contexto_forcado" in caso:
            contexto = caso["contexto_forcado"]
            fontes = []
        else:
            documentos = buscar_contexto(caso["pergunta"], vector_store, k=k)
            contexto = formatar_contexto_com_citacao(documentos)
            fontes = nomes_das_fontes(documentos)

        resposta = chain_rag.invoke({"pergunta": caso["pergunta"], "contexto": contexto})
        resultado["resposta"] = resposta
        resultado["fontes_recuperadas"] = fontes
        resultado["metricas"] = calcular_metricas_deterministicas(caso, resposta, fontes)

        if usar_juiz:
            nota = avaliar_com_juiz(llm_juiz, template_juiz, caso, contexto, resposta)
            resultado["juiz"] = nota
            if "recusou" in nota:
                resultado["metricas"]["recusa_correta"] = nota["recusou"] == caso.get("deve_recusar", False)
    except Exception as erro:
        resultado["erro"] = str(erro)
    return resultado


# ------------------------------------------------------------------- resumo

def media(valores):
    valores = [v for v in valores if v is not None]
    return round(sum(valores) / len(valores), 3) if valores else None


def resumir(resultados: list[dict]) -> dict:
    def coletar(chave_metrica):
        return [
            (1.0 if r["metricas"][chave_metrica] is True else 0.0 if r["metricas"][chave_metrica] is False else r["metricas"][chave_metrica])
            for r in resultados
            if "metricas" in r and chave_metrica in r["metricas"]
        ]

    return {
        "casos_total": len(resultados),
        "casos_com_erro": sum(1 for r in resultados if "erro" in r),
        "juiz_erros": sum(1 for r in resultados if "juiz_erro" in r.get("juiz", {})),
        "faithfulness_media": media([r["juiz"].get("faithfulness") for r in resultados if "juiz" in r]),
        "answer_relevancy_media": media([r["juiz"].get("answer_relevancy") for r in resultados if "juiz" in r]),
        "context_hit_rate": media(coletar("context_hit")),
        "citation_rate": media(coletar("citation_present")),
        "fonte_correta_rate": media(coletar("fonte_correta")),
        "fact_recall_media": media(coletar("fact_recall")),
        "injection_resistido_rate": media(coletar("injection_resistido")),
        "recusa_correta_rate": media(coletar("recusa_correta")),
    }


# --------------------------------------------------------------------- main

def rodar(iteracao, versao_prompt, k, usar_juiz, vector_store, llm_resposta, llm_juiz,
          config_extra=None, nome_eval_set="rag_eval_set.json"):
    eval_set = carregar_eval_set(nome_eval_set)
    template_juiz = carregar_prompt_juiz()
    chain_rag = construir_chain_rag(llm_resposta, versao_prompt=versao_prompt)

    resultados = []
    for caso in eval_set["casos"]:
        r = avaliar_caso(caso, vector_store, chain_rag, llm_juiz, template_juiz, k, usar_juiz)
        resultados.append(r)
        status = "ERRO" if "erro" in r else "ok"
        print(f"  [{status}] {caso['id']} - {caso['pergunta'][:55]}")

    saida = {
        "iteracao": iteracao,
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "config": {"prompt_rag": versao_prompt, "k": k, "usou_juiz": usar_juiz, **(config_extra or {})},
        "resumo": resumir(resultados),
        "resultados": resultados,
    }
    return saida


def main():
    if len(sys.argv) == 1:
        sys.exit(
            "Este script roda a partir do terminal e precisa de argumentos.\n"
            "  Rode o eval da iteração (grava em evals/rag_results_iter<N>.json):\n"
            "    python evals/run_rag_evals.py --iteracao 1 --prompt v1 --k 4\n"
            "    python evals/run_rag_evals.py --iteracao 2 --prompt v2 --k 4\n"
            "  Sem o avaliador (só métricas determinísticas):\n"
            "    python evals/run_rag_evals.py --iteracao 1 --sem-juiz"
        )
    parser = argparse.ArgumentParser(description="Roda o eval set do RAG")
    parser.add_argument("--iteracao", type=int, required=True)
    parser.add_argument("--prompt", default="v1", help="versão do prompt RAG (v1, v2, ...)")
    parser.add_argument("--k", type=int, default=4, help="chunks recuperados por pergunta")
    parser.add_argument("--sem-juiz", action="store_true", help="não chama o LLM avaliador")
    parser.add_argument("--eval-set", default="rag_eval_set.json",
                        help="arquivo do eval set dentro de evals/ (padrão: rag_eval_set.json)")
    args = parser.parse_args()

    from chain.builder import criar_llm
    from rag.chunking import CHUNK_SIZE, CHUNK_OVERLAP
    from rag.embeddings import criar_embeddings
    from rag.vector_store import carregar_vector_store

    vector_store = carregar_vector_store(criar_embeddings())
    llm_resposta = criar_llm(temperature=0)
    llm_juiz = criar_llm(temperature=0, max_tokens=1500)

    print(f"Iteração {args.iteracao} | prompt {args.prompt} | k={args.k} | eval set: {args.eval_set}")
    saida = rodar(
        args.iteracao, args.prompt, args.k, not args.sem_juiz,
        vector_store, llm_resposta, llm_juiz,
        config_extra={"chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP,
                      "modelo": "gpt-oss:120b", "temperature": 0, "embedding": "nomic-embed-text",
                      "eval_set": args.eval_set},
        nome_eval_set=args.eval_set,
    )

    caminho = PASTA_EVALS / f"rag_results_iter{args.iteracao}.json"
    caminho.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nResumo:")
    for chave, valor in saida["resumo"].items():
        print(f"  {chave}: {valor}")
    print(f"\nResultado salvo em: {caminho}")


if __name__ == "__main__":
    main()