"""
Prompt RAG -- Sprint 04, Aula 06.

Carrega o prompt RAG versionado (prompts/prompt_rag_v{N}.md) e monta a
chain completa: formata o contexto recuperado com citação de fonte, injeta
no prompt, e envia ao LLM.
"""

import sys
from pathlib import Path

PASTA_DESTE_ARQUIVO = Path(__file__).parent
PASTA_SRC = PASTA_DESTE_ARQUIVO.parent
PASTA_RAIZ = PASTA_SRC.parent
for pasta in (PASTA_DESTE_ARQUIVO, PASTA_SRC):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

PASTA_PROMPTS = PASTA_RAIZ / "prompts"


def carregar_prompt_rag(versao: str = "v1") -> str:
    """Lê prompts/prompt_rag_<versao>.md -- mesmo padrão já usado para o
    system prompt conversacional na Sprint 03 (prompts/versoes.md)."""
    caminho = PASTA_PROMPTS / f"prompt_rag_{versao}.md"
    return caminho.read_text(encoding="utf-8")


def pagina_humana(doc: Document):
    """O PyMuPDF numera páginas a partir de 0; para quem lê a citação,
    a primeira página é a 1."""
    pagina = doc.metadata.get("page")
    return pagina + 1 if isinstance(pagina, int) else "?"


def formatar_contexto_com_citacao(documentos: list[Document]) -> str:
    """
    Formata os chunks recuperados em blocos de texto citando a fonte e a
    página de cada um -- é essa formatação que alimenta a tag
    <contexto_recuperado> do prompt e permite ao modelo citar a fonte
    corretamente na resposta (grounding + citação, itens 2 e 3 do
    enunciado).
    """
    if not documentos:
        return "(Nenhum documento relevante foi encontrado na base de conhecimento.)"

    blocos = []
    for doc in documentos:
        fonte = Path(doc.metadata.get("source", "desconhecido")).name
        pagina = pagina_humana(doc)
        blocos.append(f"[Fonte: {fonte}, página {pagina}]\n{doc.page_content}")

    return "\n\n---\n\n".join(blocos)


def construir_chain_rag(llm, versao_prompt: str = "v1"):
    """
    Monta a chain RAG: prompt | llm | parser.

    Espera receber {"pergunta": str, "contexto": str} no invoke -- o
    "contexto" já deve vir formatado por formatar_contexto_com_citacao()
    antes de chegar aqui. Essa separação existe de propósito: permite
    testar a formatação do contexto e a chain em si de forma independente.
    """
    template_bruto = carregar_prompt_rag(versao_prompt)

    prompt = ChatPromptTemplate.from_messages([
        ("system", template_bruto),
        ("human", "{pergunta}"),
    ])

    return prompt | llm | StrOutputParser()


def responder_com_rag(pergunta: str, vector_store, llm, versao_prompt: str = "v1", k: int = 4) -> str:
    """
    Função de conveniência que une retriever + formatação + chain num só
    passo: busca o contexto, formata com citação, e gera a resposta.
    """
    from retriever import buscar_contexto

    documentos = buscar_contexto(pergunta, vector_store, k=k)
    contexto_formatado = formatar_contexto_com_citacao(documentos)

    chain = construir_chain_rag(llm, versao_prompt=versao_prompt)
    return chain.invoke({"pergunta": pergunta, "contexto": contexto_formatado})