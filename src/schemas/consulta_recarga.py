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
