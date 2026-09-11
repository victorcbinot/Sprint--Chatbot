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