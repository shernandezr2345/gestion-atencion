from __future__ import annotations

from typing import Any

import psycopg

from gestion_atencion.modulos.atencion.dominio.entidades import Atencion
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)
from gestion_atencion.modulos.atencion.infraestructura.excepciones import (
    DuplicidadAtencionError,
    ErrorPersistenciaAtencion,
)


class RepositorioAtencionesPostgres:
    def __init__(self, connection: psycopg.Connection):
        self._connection = connection

    def guardar(self, atencion: Atencion) -> None:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO atenciones (
                        id_atencion,
                        solicitud_id,
                        partner_id,
                        referencia_externa,
                        tipo_servicio,
                        estado,
                        fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (solicitud_id) DO NOTHING
                    """,
                    (
                        atencion.id_atencion,
                        atencion.solicitud_id.valor,
                        atencion.partner_id.valor,
                        atencion.referencia_externa.valor,
                        atencion.tipo_servicio.valor,
                        atencion.estado.value,
                        atencion.fecha_creacion,
                    ),
                )
                if cursor.rowcount == 0:
                    raise DuplicidadAtencionError(
                        f"Ya existe una atención para la solicitud {atencion.solicitud_id.valor}"
                    )
        except psycopg.IntegrityError as exc:
            raise DuplicidadAtencionError(
                f"Ya existe una atención para la solicitud {atencion.solicitud_id.valor}"
            ) from exc
        except Exception as exc:  # pragma: no cover - infraestructura
            raise ErrorPersistenciaAtencion(str(exc)) from exc

    def actualizar(self, atencion: Atencion) -> None:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE atenciones
                    SET
                        partner_id = %s,
                        referencia_externa = %s,
                        tipo_servicio = %s,
                        estado = %s
                    WHERE id_atencion = %s
                    """,
                    (
                        atencion.partner_id.valor,
                        atencion.referencia_externa.valor,
                        atencion.tipo_servicio.valor,
                        atencion.estado.value,
                        atencion.id_atencion,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ErrorPersistenciaAtencion(
                        f"No existe la atención {atencion.id_atencion} para actualizar"
                    )
        except Exception as exc:  # pragma: no cover - infraestructura
            raise ErrorPersistenciaAtencion(str(exc)) from exc

    def buscar_por_solicitud_id(self, solicitud_id: str) -> Atencion | None:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_atencion,
                        solicitud_id,
                        partner_id,
                        referencia_externa,
                        tipo_servicio,
                        estado,
                        fecha_creacion
                    FROM atenciones
                    WHERE solicitud_id = %s
                    """,
                    (solicitud_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                return self._mapear(row)
        except Exception as exc:  # pragma: no cover - infraestructura
            raise ErrorPersistenciaAtencion(str(exc)) from exc

    @staticmethod
    def _mapear(row: Any) -> Atencion:
        return Atencion(
            id_atencion=row[0],
            solicitud_id=SolicitudId(row[1]),
            partner_id=PartnerId(row[2]),
            referencia_externa=ReferenciaExterna(row[3]),
            tipo_servicio=TipoServicio(row[4]),
            estado=EstadoAtencion(row[5]),
            fecha_creacion=row[6],
        )
