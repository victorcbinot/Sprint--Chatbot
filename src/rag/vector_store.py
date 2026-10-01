"""
Vector store -- Sprint 04 (RAG), Aula 05.

Usa ChromaDB persistente (grava em disco, não só em memória) para armazenar
os embeddings dos chunks da base de conhecimento, permitindo busca semântica
sem precisar reprocessar os PDFs a cada execução do chatbot.
"""

from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

PASTA_CHROMA = Path(__file__).parent.parent.parent / "data" / "chroma_db"
NOME_COLECAO = "chargegrid_knowledge_base"


def construir_vector_store(chunks: list[Document], embeddings: Embeddings) -> Chroma:
    """
    Cria (ou recria) o vector store persistente a partir dos chunks da base
    de conhecimento. Deve ser rodado sempre que a base de conhecimento
    (PDFs em data/knowledge_base/) mudar.
    """
    PASTA_CHROMA.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=NOME_COLECAO,
        persist_directory=str(PASTA_CHROMA),
    )


def carregar_vector_store(embeddings: Embeddings) -> Chroma:
    """
    Carrega o vector store já persistido em disco, sem precisar reprocessar
    os PDFs. Usado pelo pipeline RAG em tempo de execução (quando o
    operador faz uma pergunta ao chatbot).
    """
    if not PASTA_CHROMA.exists():
        raise FileNotFoundError(
            f"Vector store não encontrado em {PASTA_CHROMA}. "
            "Rode indexar_base_de_conhecimento.py primeiro."
        )
    return Chroma(
        collection_name=NOME_COLECAO,
        embedding_function=embeddings,
        persist_directory=str(PASTA_CHROMA),
    )