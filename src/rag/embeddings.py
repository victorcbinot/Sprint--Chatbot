"""
Embeddings -- Sprint 04 (RAG), Aula 05.

Usa nomic-embed-text para gerar os vetores de embedding dos chunks da base
de conhecimento e das perguntas do operador.

IMPORTANTE -- por que isso roda LOCAL, diferente do chat (builder.py):
Testamos nomic-embed-text via Ollama Cloud e recebemos 401 (unauthorized)
mesmo com a mesma API key que funciona para chat. Pesquisando, confirmamos
que é uma limitação conhecida da plataforma: o Ollama Cloud hoje expõe
apenas modelos de CHAT pela API -- embeddings não estão disponíveis na
nuvem, nem em planos pagos (ver issue ollama/ollama#17129 no GitHub).

Solução adotada: embeddings rodam no Ollama LOCAL (instalado na máquina do
usuário, gratuito, sem precisar de API key), enquanto o chat continua
usando o Ollama Cloud (builder.py). É uma combinação totalmente suportada
-- só não dá para fazer as duas coisas 100% em nuvem com o Ollama hoje.

Pré-requisito (rodar uma vez, na máquina onde o projeto for executado):
    ollama pull nomic-embed-text
"""

from langchain_ollama import OllamaEmbeddings


def criar_embeddings() -> OllamaEmbeddings:
    """
    Cria o cliente de embeddings via Ollama LOCAL (http://localhost:11434,
    padrão da lib -- não precisa de base_url nem de API key).

    Requer Ollama instalado e rodando localmente, com o modelo já baixado
    (`ollama pull nomic-embed-text`).
    """
    return OllamaEmbeddings(model="nomic-embed-text")