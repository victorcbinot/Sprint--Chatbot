"""
Testa o pipeline RAG inteiro, passo a passo, com mensagens claras de
sucesso/erro em cada etapa. Use isto para confirmar que tudo está
funcionando na sua máquina antes de integrar com o chatbot.

Requer OLLAMA_API_KEY configurada no .env (etapas 3 e 4 fazem chamadas
reais ao Ollama Cloud).

Uso:
    python src/rag/testar_pipeline_rag.py
"""

import sys
from pathlib import Path

PASTA_DESTE_ARQUIVO = Path(__file__).parent
PASTA_SRC = PASTA_DESTE_ARQUIVO.parent
for pasta in (PASTA_DESTE_ARQUIVO, PASTA_SRC):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))


def etapa(numero, nome):
    print(f"\n{'='*60}\nEtapa {numero}: {nome}\n{'='*60}")


def ok(msg):
    print(f"  OK: {msg}")


def erro(msg):
    print(f"  ERRO: {msg}")


def main():
    # Etapa 1: loader
    etapa(1, "Carregando PDFs da base de conhecimento")
    try:
        from loader import carregar_base_de_conhecimento
        documentos = carregar_base_de_conhecimento()
        if len(documentos) == 0:
            erro("Nenhum documento carregado -- confira se há PDFs em data/knowledge_base/")
            return
        ok(f"{len(documentos)} documento(s) carregado(s)")
        for d in documentos:
            print(f"    - {Path(d.metadata['source']).name} (página {d.metadata['page']})")
    except Exception as e:
        erro(f"Falha ao carregar PDFs: {e}")
        return

    # Etapa 2: chunking
    etapa(2, "Dividindo em chunks")
    try:
        from chunking import dividir_em_chunks
        chunks = dividir_em_chunks(documentos)
        if len(chunks) == 0:
            erro("Nenhum chunk gerado -- algo está errado no chunking")
            return
        ok(f"{len(chunks)} chunk(s) gerado(s) a partir de {len(documentos)} documento(s)")
    except Exception as e:
        erro(f"Falha no chunking: {e}")
        return

    # Etapa 3: embeddings (chamada real ao Ollama)
    etapa(3, "Testando embeddings (chamada real ao Ollama Cloud)")
    try:
        from embeddings import criar_embeddings
        emb = criar_embeddings()
        vetor_teste = emb.embed_query("teste de conexão")
        ok(f"Embedding gerado com sucesso (dimensão do vetor: {len(vetor_teste)})")
    except Exception as e:
        erro(f"Falha ao gerar embedding: {e}")
        print("  Confira se OLLAMA_API_KEY está configurada corretamente no .env")
        return

    # Etapa 4: vector store (indexação completa)
    etapa(4, "Indexando a base de conhecimento no ChromaDB")
    try:
        from vector_store import construir_vector_store
        vs = construir_vector_store(chunks, emb)
        total = vs._collection.count()
        ok(f"Vector store criado/atualizado com {total} chunk(s) indexado(s)")
    except Exception as e:
        erro(f"Falha ao indexar: {e}")
        return

    # Etapa 5: busca semântica de verdade
    etapa(5, "Testando busca semântica")
    perguntas_teste = [
        "Como funciona o Smart Charging?",
        "Posso reservar um horário no carregador?",
        "Qual a tarifa no horário de pico?",
    ]
    try:
        for pergunta in perguntas_teste:
            resultados = vs.similarity_search(pergunta, k=2)
            print(f"\n  Pergunta: \"{pergunta}\"")
            for r in resultados:
                fonte = Path(r.metadata["source"]).name
                trecho = r.page_content[:100].replace("\n", " ")
                print(f"    -> {fonte}: \"{trecho}...\"")
        ok("Busca semântica funcionando")
    except Exception as e:
        erro(f"Falha na busca semântica: {e}")
        return

    print(f"\n{'='*60}")
    print("TUDO FUNCIONANDO. O pipeline RAG está pronto para o próximo passo")
    print("(integrar com a chain conversacional).")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()