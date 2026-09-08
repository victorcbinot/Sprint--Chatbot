from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StatusCarregador(str, Enum):

    ATIVO = "ativo"
    FALHA = "falha"
    MANUTENCAO = "manutencao"
    INDISPONIVEL = "indisponivel"


class ConsultaRecarga(BaseModel):

    carregador_id: int = Field(
        ...,
        description="Identificador do carregador consultado (1 a 5, conforme o layout atual da estação).",
        ge=1,
        le=5,
    )
    status: StatusCarregador = Field(
        ...,
        description="Estado atual do carregador.",
    )
    potencia_kw: float = Field(
        ...,
        description="Consumo de potência do carregador em kW no momento da consulta.",
        ge=0,
    )
    sessoes_ativas: int = Field(
        default=0,
        description="Número de sessões de carregamento ativas neste carregador.",
        ge=0,
    )
    observacao: Optional[str] = Field(
        default=None,
        description="Detalhe adicional em texto livre, ex.: motivo de uma falha.",
        validate_default=True,
    )

    @field_validator("observacao")
    @classmethod
    def observacao_obrigatoria_se_falha(cls, valor: Optional[str], info) -> Optional[str]:

        status = info.data.get("status")
        if status == StatusCarregador.FALHA and not valor:
            raise ValueError(
                "observacao é obrigatória quando status='falha' "
                "(é preciso registrar o motivo da falha)."
            )
        return valor

    @field_validator("potencia_kw")
    @classmethod
    def potencia_dentro_da_capacidade(cls, valor: float) -> float:

        CAPACIDADE_CONTRATADA_KW = 96.0
        if valor > CAPACIDADE_CONTRATADA_KW:
            raise ValueError(
                f"potencia_kw ({valor}) excede a capacidade contratada "
                f"da estação ({CAPACIDADE_CONTRATADA_KW} kW)."
            )
        return valor


if __name__ == "__main__":

    # 1) Caso válido
    consulta_ok = ConsultaRecarga(
        carregador_id=1,
        status=StatusCarregador.ATIVO,
        potencia_kw=17.4,
        sessoes_ativas=1,
    )
    print("Consulta válida:")
    print(consulta_ok.model_dump_json(indent=2))

    # 2) Caso que deveria FALHAR: status=falha sem observação
    print("\nTentando criar consulta inválida (falha sem observação)...")
    try:
        ConsultaRecarga(
            carregador_id=2,
            status=StatusCarregador.FALHA,
            potencia_kw=0,
        )
    except Exception as erro:
        print("Erro esperado:", erro)

    # 3) Caso que deveria FALHAR: potência acima da capacidade contratada
    print("\nTentando criar consulta inválida (potência acima da capacidade)...")
    try:
        ConsultaRecarga(
            carregador_id=3,
            status=StatusCarregador.ATIVO,
            potencia_kw=150,
        )
    except Exception as erro:
        print("Erro esperado:", erro)