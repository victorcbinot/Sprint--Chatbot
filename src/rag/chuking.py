"""
Chunking da base de conhecimento -- Sprint 04 (RAG).

Usa RecursiveCharacterTextSplitter (Aula 06) para dividir os documentos
carregados em pedaços menores antes de gerar embeddings.

Decisão de chunk_size/overlap (documentada também em docs/relatorio_rag.md):
- chunk_size=500: os documentos da base são curtos e densos (manual técnico,
  FAQ, regimento, tabela tarifária) -- pedaços muito grandes misturariam
  tópicos diferentes (ex.: Smart Charging + manutenção preventiva no mesmo
  chunk), prejudicando a precisão da recuperação.
- chunk_overlap=50: overlap pequeno o suficiente para não inflar demais o
  número de chunks, mas suficiente para não cortar uma frase-chave bem no
  meio da divisão entre dois chunks.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def dividir_em_chunks(documentos: list[Document]) -> list[Document]:
    """
    Divide uma lista de Document (tipicamente uma página de PDF cada) em
    chunks menores, preservando os metadados originais (source, page) em
    cada chunk -- essencial para a citação de fonte.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documentos)
