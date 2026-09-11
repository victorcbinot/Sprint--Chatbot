

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import trim_messages


LIMITE_TOKENS_HISTORICO = 500
_HISTORICOS_POR_SESSAO: dict[str, InMemoryChatMessageHistory] = {}


def obter_historico_da_sessao(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _HISTORICOS_POR_SESSAO:
        _HISTORICOS_POR_SESSAO[session_id] = InMemoryChatMessageHistory()
    return _HISTORICOS_POR_SESSAO[session_id]


def aplicar_limite_de_tokens(session_id: str) -> None:
    historico = obter_historico_da_sessao(session_id)
    mensagens_cortadas = trim_messages(
        historico.messages,
        max_tokens=LIMITE_TOKENS_HISTORICO,
        token_counter="approximate",
        strategy="last",
        start_on="human",
        include_system=True,
    )
    historico.clear()
    for mensagem in mensagens_cortadas:
        historico.add_message(mensagem)


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, AIMessage

    session_id = "sessao_teste"
    historico = obter_historico_da_sessao(session_id)


    turnos = [
        ("Qual o status do carregador 2?", "O carregador 2 está em falha de comunicação OCPP."),
        ("Qual o consumo atual da estação?", "O consumo atual é de 87 kW."),
        ("Quantas sessões estão ativas?", "Existem 3 sessões de carregamento ativas."),
        ("E o carregador 5?", "O carregador 5 está em manutenção preventiva."),
        ("Qual a capacidade contratada?", "A capacidade contratada é de 96 kW."),
    ]

    for pergunta, resposta in turnos:
        historico.add_message(HumanMessage(content=pergunta))
        historico.add_message(AIMessage(content=resposta))

    print(f"Mensagens antes do corte: {len(historico.messages)}")
    print(f"(limite configurado: {LIMITE_TOKENS_HISTORICO} tokens -- com 5 turnos curtos, "
          f"pode não haver corte; isso é esperado e correto)\n")

    aplicar_limite_de_tokens(session_id)

    print(f"Mensagens depois do corte (limite={LIMITE_TOKENS_HISTORICO}): {len(historico.messages)}")
    for m in historico.messages:
        print(f"  [{m.type}] {m.content}")


    print("\n--- Demonstração do corte com limite mais apertado (30 tokens) ---")
    historico_demo = InMemoryChatMessageHistory()
    for pergunta, resposta in turnos:
        historico_demo.add_message(HumanMessage(content=pergunta))
        historico_demo.add_message(AIMessage(content=resposta))

    mensagens_cortadas_demo = trim_messages(
        historico_demo.messages,
        max_tokens=30,
        token_counter="approximate",
        strategy="last",
        start_on="human",
        include_system=True,
    )
    print(f"Mensagens antes: {len(historico_demo.messages)} | depois do corte: {len(mensagens_cortadas_demo)}")
    for m in mensagens_cortadas_demo:
        print(f"  [{m.type}] {m.content}")