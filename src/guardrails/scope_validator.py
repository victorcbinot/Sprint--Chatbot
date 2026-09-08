from dataclasses import dataclass
from enum import Enum


class TipoRecusa(str, Enum):
    FORA_DE_ESCOPO = "fora_de_escopo"
    ACONSELHAMENTO_JURIDICO = "aconselhamento_juridico"
    ACONSELHAMENTO_FINANCEIRO = "aconselhamento_financeiro"
    SEGURANCA_ELETRICA = "seguranca_eletrica"


@dataclass
class ResultadoValidacaoEscopo:
    dentro_do_escopo: bool
    tipo_recusa: TipoRecusa | None = None
    mensagem: str | None = None



PALAVRAS_DOMINIO_EV = [
    "carregador", "carregadores", "recarga", "carga", "eletroposto",
    "estação", "consumo", "potência", "kw", "smart charging",
    "sessão", "sessões", "ocpp", "veículo", "veiculo", "bateria",
    "falha", "manutenção", "faturamento operacional",
]


PALAVRAS_JURIDICO = [
    "processo judicial", "posso processar", "aconselhamento jurídico",
    "advogado", "contrato legal", "multa jurídica", "ação judicial",
]


PALAVRAS_FINANCEIRO = [
    "investir", "investimento", "ação da bolsa", "vale a pena comprar",
    "aconselhamento financeiro", "declarar imposto de renda",
]


PALAVRAS_SEGURANCA_ELETRICA = [
    "posso mexer no disjuntor", "como fazer a instalação elétrica",
    "é seguro eu mesmo", "risco de choque", "fiação",
]

MENSAGENS_RECUSA = {
    TipoRecusa.FORA_DE_ESCOPO: (
        "Essa pergunta está fora do escopo do ChargeGrid Assistant. "
        "Posso ajudar com status de carregadores, consumo energético, "
        "Smart Charging, sessões de recarga e falhas operacionais."
    ),
    TipoRecusa.ACONSELHAMENTO_JURIDICO: (
        "Não posso fornecer aconselhamento jurídico. Para questões legais "
        "relacionadas à operação do eletroposto, recomendo consultar um "
        "advogado habilitado."
    ),
    TipoRecusa.ACONSELHAMENTO_FINANCEIRO: (
        "Não posso fornecer aconselhamento financeiro ou de investimento. "
        "Para essas decisões, recomendo consultar um profissional de "
        "contabilidade ou finanças habilitado."
    ),
    TipoRecusa.SEGURANCA_ELETRICA: (
        "Não posso orientar sobre intervenção em instalações elétricas. "
        "Por segurança, esse tipo de procedimento deve ser feito por um "
        "engenheiro eletricista habilitado."
    ),
}


def _contem_alguma(texto: str, palavras: list[str]) -> bool:
    texto_normalizado = texto.lower()
    return any(palavra in texto_normalizado for palavra in palavras)


def validar_escopo(pergunta: str) -> ResultadoValidacaoEscopo:

    if _contem_alguma(pergunta, PALAVRAS_JURIDICO):
        return ResultadoValidacaoEscopo(
            dentro_do_escopo=False,
            tipo_recusa=TipoRecusa.ACONSELHAMENTO_JURIDICO,
            mensagem=MENSAGENS_RECUSA[TipoRecusa.ACONSELHAMENTO_JURIDICO],
        )

    if _contem_alguma(pergunta, PALAVRAS_FINANCEIRO):
        return ResultadoValidacaoEscopo(
            dentro_do_escopo=False,
            tipo_recusa=TipoRecusa.ACONSELHAMENTO_FINANCEIRO,
            mensagem=MENSAGENS_RECUSA[TipoRecusa.ACONSELHAMENTO_FINANCEIRO],
        )

    if _contem_alguma(pergunta, PALAVRAS_SEGURANCA_ELETRICA):
        return ResultadoValidacaoEscopo(
            dentro_do_escopo=False,
            tipo_recusa=TipoRecusa.SEGURANCA_ELETRICA,
            mensagem=MENSAGENS_RECUSA[TipoRecusa.SEGURANCA_ELETRICA],
        )

    if _contem_alguma(pergunta, PALAVRAS_DOMINIO_EV):
        return ResultadoValidacaoEscopo(dentro_do_escopo=True)

    return ResultadoValidacaoEscopo(
        dentro_do_escopo=False,
        tipo_recusa=TipoRecusa.FORA_DE_ESCOPO,
        mensagem=MENSAGENS_RECUSA[TipoRecusa.FORA_DE_ESCOPO],
    )


if __name__ == "__main__":
    perguntas_teste = [
        "Qual o status do carregador 2?",
        "Qual a capital da França?",
        "O carregador pegou fogo, posso processar a GoodWe?",
        "Vale a pena investir em ações da GoodWe?",
        "Posso mexer no disjuntor sozinho para resolver a falha?",
    ]

    for pergunta in perguntas_teste:
        resultado = validar_escopo(pergunta)
        print(f"Pergunta: {pergunta}")
        print(f"  Dentro do escopo: {resultado.dentro_do_escopo}")
        if not resultado.dentro_do_escopo:
            print(f"  Tipo de recusa: {resultado.tipo_recusa.value}")
            print(f"  Mensagem: {resultado.mensagem}")
        print()