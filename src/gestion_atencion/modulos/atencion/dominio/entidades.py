"""Aggregate Root Atencion."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from gestion_atencion.modulos.atencion.dominio.excepciones import EstadoTransicionInvalidaError
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)


@dataclass(frozen=True)
class Atencion:
    """Aggregate Root de Gestión de Atención."""

    id_atencion: str
    solicitud_id: SolicitudId
    partner_id: PartnerId
    referencia_externa: ReferenciaExterna
    tipo_servicio: TipoServicio
    estado: EstadoAtencion
    fecha_creacion: datetime

    @classmethod
    def crear(
        cls,
        solicitud_id: SolicitudId,
        partner_id: PartnerId,
        referencia_externa: ReferenciaExterna,
        tipo_servicio: TipoServicio,
    ) -> "Atencion":
        return cls(
            id_atencion=str(uuid.uuid4()),
            solicitud_id=solicitud_id,
            partner_id=partner_id,
            referencia_externa=referencia_externa,
            tipo_servicio=tipo_servicio,
            estado=EstadoAtencion.PENDIENTE,
            fecha_creacion=datetime.now(timezone.utc),
        )

    def cambiar_estado_a_en_atencion(self) -> None:
        self._validar_transicion(EstadoAtencion.EN_ATENCION)
        object.__setattr__(self, "estado", EstadoAtencion.EN_ATENCION)

    def cerrar(self) -> None:
        self._validar_transicion(EstadoAtencion.CERRADA)
        object.__setattr__(self, "estado", EstadoAtencion.CERRADA)

    def puede_cambiar_estado_a(self, nuevo_estado: EstadoAtencion) -> bool:
        try:
            self._validar_transicion(nuevo_estado)
            return True
        except EstadoTransicionInvalidaError:
            return False

    def _validar_transicion(self, nuevo_estado: EstadoAtencion) -> None:
        transiciones_validas = {
            EstadoAtencion.PENDIENTE: {EstadoAtencion.EN_ATENCION},
            EstadoAtencion.EN_ATENCION: {EstadoAtencion.CERRADA},
            EstadoAtencion.CERRADA: set(),
        }

        if nuevo_estado not in transiciones_validas.get(self.estado, set()):
            raise EstadoTransicionInvalidaError(
                f"No se permite la transición {self.estado.value} -> {nuevo_estado.value}"
            )
