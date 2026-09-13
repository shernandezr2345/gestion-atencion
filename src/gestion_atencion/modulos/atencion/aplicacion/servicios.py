"""Casos de uso de la capa de aplicación para Gestión de Atención."""

from __future__ import annotations

from gestion_atencion.modulos.atencion.aplicacion.excepciones import (
    AtencionNoEncontradaError,
    AtencionYaExisteError,
)
from gestion_atencion.modulos.atencion.dominio.entidades import Atencion
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)


class CrearAtencion:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(
        self,
        solicitud_id: str,
        partner_id: str,
        referencia_externa: str,
        tipo_servicio: str,
    ) -> Atencion:
        existente = self._repositorio.buscar_por_solicitud_id(solicitud_id)
        if existente is not None:
            raise AtencionYaExisteError(
                f"Ya existe una atención para la solicitud {solicitud_id}"
            )

        atencion = Atencion.crear(
            solicitud_id=SolicitudId(solicitud_id),
            partner_id=PartnerId(partner_id),
            referencia_externa=ReferenciaExterna(referencia_externa),
            tipo_servicio=TipoServicio(tipo_servicio),
        )

        self._repositorio.guardar(atencion)
        return atencion


class CambiarEstadoAtencion:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def ejecutar(self, solicitud_id: str, nuevo_estado: EstadoAtencion) -> Atencion:
        atencion = self._repositorio.buscar_por_solicitud_id(solicitud_id)
        if atencion is None:
            raise AtencionNoEncontradaError(
                f"No existe una atención para la solicitud {solicitud_id}"
            )

        if nuevo_estado == EstadoAtencion.EN_ATENCION:
            atencion.cambiar_estado_a_en_atencion()
        elif nuevo_estado == EstadoAtencion.CERRADA:
            atencion.cerrar()
        else:
            raise ValueError(f"Estado no soportado: {nuevo_estado}")

        self._repositorio.actualizar(atencion)
        return atencion
