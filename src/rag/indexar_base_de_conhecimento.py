"""
Indexa a base de conhecimento -- Sprint 04 (RAG).

Roda o pipeline completo de vetorização: carrega os PDFs, divide em chunks,
gera embeddings via Ollama Cloud (nomic-embed-text) e salva no ChromaDB
persistente (data/chroma_db/).

Rodar sempre que a base de conhecimento (data/knowledge_base/) mudar.

Uso:
    python src/rag/indexar_base_de_conhecimento.py
"""

import sys
from pathlib import Path

PASTA_DESTE_ARQUIVO = Path(__file__).parent
PASTA_SRC = PASTA_DESTE_ARQUIVO.parent
for pasta in (PASTA_DESTE_ARQUIVO, PASTA_SRC):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

from loader import carregar_base_de_conhecimento
from chunking import dividir_em_chunks
from embeddings import criar_embeddings
from vector_store import construir_vector_store


def indexar():
    print("1/3 - Carregando PDFs de data/knowledge_base/...")
    documentos = carregar_base_de_conhecimento()
    print(f"      {len(documentos)} documento(s) carregado(s).")

    print("2/3 - Dividindo em chunks...")
    chunks = dividir_em_chunks(documentos)
    print(f"      {len(chunks)} chunk(s) gerado(s).")

    print("3/3 - Gerando embeddings e salvando no ChromaDB (requer OLLAMA_API_KEY)...")
    embeddings = criar_embeddings()
    vector_store = construir_vector_store(chunks, embeddings)
    print("      Vector store criado/atualizado com sucesso.")

    return vector_store


if __name__ == "__main__":
    indexar()