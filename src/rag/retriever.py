"""
Retriever -- Sprint 04 (RAG), Aula 06.

Encapsula a busca semântica no vector store: dado uma pergunta, retorna os
chunks mais relevantes da base de conhecimento.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document

K_PADRAO = 4  # quantos chunks recuperar por pergunta


def buscar_contexto(pergunta: str, vector_store: Chroma, k: int = K_PADRAO) -> list[Document]:
    """
    Busca os k chunks mais relevantes para a pergunta no vector store.
    k=4 foi escolhido como ponto de partida -- documentado em
    docs/relatorio_rag.md junto com o resultado da avaliação (ganho ou
    perda ao ajustar esse valor faz parte do processo de iteração exigido
    pelo enunciado).
    """
    return vector_store.similarity_search(pergunta, k=k)