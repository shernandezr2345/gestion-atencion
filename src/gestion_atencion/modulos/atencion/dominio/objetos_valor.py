

"""Estado del Aggregate Atencion."""

from enum import Enum


class EstadoAtencion(str, Enum):
    """Estados mínimos del agregado de atención."""

    PENDIENTE = "PENDIENTE"
    EN_ATENCION = "EN_ATENCION"
    CERRADA = "CERRADA"



"""Identificador del partner asociado."""

from dataclasses import dataclass


def _validar_texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ValueError(f"{nombre} debe ser un texto")
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre} es obligatorio")
    return texto


@dataclass(frozen=True)
class PartnerId:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", _validar_texto(self.valor, "partner_id"))



"""Referencia externa de la solicitud."""

from dataclasses import dataclass


def _validar_texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ValueError(f"{nombre} debe ser un texto")
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre} es obligatorio")
    return texto


@dataclass(frozen=True)
class ReferenciaExterna:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", _validar_texto(self.valor, "referencia_externa"))



"""Identificador de la solicitud asociada."""

from dataclasses import dataclass


def _validar_texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ValueError(f"{nombre} debe ser un texto")
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre} es obligatorio")
    return texto


@dataclass(frozen=True)
class SolicitudId:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", _validar_texto(self.valor, "solicitud_id"))



"""Tipo de servicio solicitado."""

from dataclasses import dataclass


def _validar_texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ValueError(f"{nombre} debe ser un texto")
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre} es obligatorio")
    return texto


@dataclass(frozen=True)
class TipoServicio:
    valor: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "valor", _validar_texto(self.valor, "tipo_servicio"))

