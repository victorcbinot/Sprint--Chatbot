import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings

load_dotenv()


def criar_embeddings() -> OllamaEmbeddings:
    """
    Cria o cliente de embeddings via Ollama Cloud, usando o modelo
    nomic-embed-text (Aula 05) -- especializado em gerar vetores de texto
    para busca semântica, diferente do gpt-oss:120b (que gera texto).
    """
    api_key = os.getenv("OLLAMA_API_KEY")
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {"Authorization": f"Bearer {api_key}"},
        },
    )