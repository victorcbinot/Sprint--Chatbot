

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama

PASTA_DESTE_ARQUIVO = Path(__file__).parent
PASTA_SRC = PASTA_DESTE_ARQUIVO.parent
for pasta in (PASTA_DESTE_ARQUIVO, PASTA_SRC):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

from memoria import obter_historico_da_sessao, aplicar_limite_de_tokens
from schemas.consulta_recarga import ConsultaRecarga

load_dotenv()

RAIZ_DO_PROJETO = PASTA_SRC.parent
PASTA_PROMPTS = RAIZ_DO_PROJETO / "prompts"


def carregar_prompt(versao: str = "v2") -> str:
    caminho = PASTA_PROMPTS / f"system_prompt_{versao}.md"
    return caminho.read_text(encoding="utf-8")


def criar_llm(
        model: str = "gpt-oss:120b",
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 512,
) -> ChatOllama:
    """
    Cria o cliente do modelo via Ollama Cloud, mesma configuração que
    já era usada no chatbot.py da Sprint 2 (host + Authorization Bearer),
    só que agora encapsulado no ChatOllama do LangChain em vez do client
    cru da lib `ollama`.

    Parâmetros expostos (documentados em docs/relatorio_modelos.md):
      - model: qual modelo usar no Ollama Cloud (ex.: "gpt-oss:120b",
        "qwen3:8b"). Poder trocar o modelo aqui é o que permite comparar
        modelos diferentes sem duplicar código (e atende o item bônus do
        enunciado: chamada com mais de um modelo).
      - temperature: 0 = respostas mais determinísticas/previsíveis;
        valores maiores = mais variação entre execuções.
      - top_p: nucleus sampling -- restringe a escolha de tokens ao
        conjunto que soma essa probabilidade acumulada.
      - max_tokens: limite de tamanho da resposta gerada.
    """
    api_key = os.getenv("OLLAMA_API_KEY")
    return ChatOllama(
        model=model,
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {"Authorization": f"Bearer {api_key}"},
        },
        temperature=temperature,
        top_p=top_p,
        num_predict=max_tokens,
    )


def construir_chain_conversacional(versao_prompt: str = "v2"):
    system_prompt = carregar_prompt(versao_prompt)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="historico"),
        ("human", "{pergunta}"),
    ])

    llm = criar_llm()

    chain_base = prompt | llm | StrOutputParser()

    chain_com_memoria = RunnableWithMessageHistory(
        chain_base,
        obter_historico_da_sessao,
        input_messages_key="pergunta",
        history_messages_key="historico",
    )

    return chain_com_memoria


def perguntar(chain, pergunta: str, session_id: str) -> str:

    resposta = chain.invoke(
        {"pergunta": pergunta},
        config={"configurable": {"session_id": session_id}},
    )
    aplicar_limite_de_tokens(session_id)
    return resposta


def consultar_estruturado(pergunta: str, versao_prompt: str = "v2") -> ConsultaRecarga:

    llm = criar_llm(temperature=0)

    llm_estruturado = llm.with_structured_output(ConsultaRecarga)

    system_prompt = carregar_prompt(versao_prompt)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        ("human", "{pergunta}"),
    ])

    chain = prompt | llm_estruturado
    return chain.invoke({"pergunta": pergunta})


if __name__ == "__main__":
    print("Este arquivo depende de uma chamada real ao Ollama Cloud "
          "(precisa de OLLAMA_API_KEY configurada no .env).")
    print("Para testar a lógica da chain sem depender do Ollama, "
          "veja testar_chain_com_fake_llm.py na mesma pasta.\n")

    print("Exemplo de uso real (requer .env configurado):")
    print("""
    chain = construir_chain_conversacional()
    resposta1 = perguntar(chain, "Qual o status do carregador 2?", session_id="op1")
    resposta2 = perguntar(chain, "E o consumo atual?", session_id="op1")
    print(resposta1)
    print(resposta2)

    consulta = consultar_estruturado("Qual o status do carregador 2?")
    print(consulta.model_dump_json(indent=2))
    """)