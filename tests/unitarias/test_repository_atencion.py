import uuid

import pytest

from gestion_atencion.modulos.atencion.dominio.entidades import Atencion
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)
from gestion_atencion.modulos.atencion.infraestructura.excepciones import DuplicidadAtencionError
from gestion_atencion.modulos.atencion.infraestructura.repositorios import RepositorioAtencionesPostgres


@pytest.fixture
def repo_db(monkeypatch):
    registros = {}

    class Cursor:
        def __init__(self, registros):
            self.registros = registros
            self.rowcount = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, query, params=()):
            if "INSERT INTO atenciones" in query:
                key = params[1]
                if key in self.registros:
                    self.rowcount = 0
                    raise ValueError("duplicado")
                self.registros[key] = {
                    "id_atencion": params[0],
                    "solicitud_id": params[1],
                    "partner_id": params[2],
                    "referencia_externa": params[3],
                    "tipo_servicio": params[4],
                    "estado": params[5],
                    "fecha_creacion": params[6],
                }
                self.rowcount = 1
                return

            if "UPDATE atenciones" in query:
                id_atencion = params[-1]
                row = next((valor for valor in self.registros.values() if valor["id_atencion"] == id_atencion), None)
                if row is None:
                    self.rowcount = 0
                    return
                row["partner_id"] = params[0]
                row["referencia_externa"] = params[1]
                row["tipo_servicio"] = params[2]
                row["estado"] = params[3]
                self.rowcount = 1
                return

            if "SELECT" in query and "FROM atenciones" in query:
                key = params[0]
                if key not in self.registros:
                    self.rowcount = 0
                    self._last_row = None
                    return
                self.rowcount = 1
                row = self.registros[key]
                self._last_row = (
                    row["id_atencion"],
                    row["solicitud_id"],
                    row["partner_id"],
                    row["referencia_externa"],
                    row["tipo_servicio"],
                    row["estado"],
                    row["fecha_creacion"],
                )
                return

        def fetchone(self):
            return getattr(self, "_last_row", None)

    class Connection:
        def __init__(self):
            self._registros = registros

        def cursor(self):
            return Cursor(self._registros)

    return RepositorioAtencionesPostgres(Connection())


def test_guardar_atencion_correctamente(repo_db):
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-001"),
        partner_id=PartnerId("partner-001"),
        referencia_externa=ReferenciaExterna("REF-001"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )

    repo_db.guardar(atencion)

    guardada = repo_db.buscar_por_solicitud_id("sol-001")

    assert guardada is not None
    assert guardada.solicitud_id == SolicitudId("sol-001")
    assert guardada.estado == EstadoAtencion.PENDIENTE


def test_consultar_atencion_por_solicitud_id(repo_db):
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-002"),
        partner_id=PartnerId("partner-002"),
        referencia_externa=ReferenciaExterna("REF-002"),
        tipo_servicio=TipoServicio("MANTENIMIENTO"),
    )
    atencion.cambiar_estado_a_en_atencion()

    repo_db.guardar(atencion)
    encontrada = repo_db.buscar_por_solicitud_id("sol-002")

    assert encontrada is not None
    assert encontrada.estado == EstadoAtencion.EN_ATENCION


def test_no_permite_dos_atenciones_con_la_misma_solicitud_id(repo_db):
    primera = Atencion.crear(
        solicitud_id=SolicitudId("sol-003"),
        partner_id=PartnerId("partner-003"),
        referencia_externa=ReferenciaExterna("REF-003"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )
    segunda = Atencion.crear(
        solicitud_id=SolicitudId("sol-003"),
        partner_id=PartnerId("partner-004"),
        referencia_externa=ReferenciaExterna("REF-004"),
        tipo_servicio=TipoServicio("REPARACION"),
    )

    repo_db.guardar(primera)

    with pytest.raises(Exception):
        repo_db.guardar(segunda)


def test_conserva_estado_pendiente_en_atencion_y_cerrada(repo_db):
    pendiente = Atencion.crear(
        solicitud_id=SolicitudId("sol-004"),
        partner_id=PartnerId("partner-004"),
        referencia_externa=ReferenciaExterna("REF-004"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )
    repo_db.guardar(pendiente)

    en_atencion = repo_db.buscar_por_solicitud_id("sol-004")
    assert en_atencion is not None
    assert en_atencion.estado == EstadoAtencion.PENDIENTE

    en_atencion.cambiar_estado_a_en_atencion()
    repo_db.actualizar(en_atencion)

    en_atencion_guardada = repo_db.buscar_por_solicitud_id("sol-004")
    assert en_atencion_guardada is not None
    assert en_atencion_guardada.estado == EstadoAtencion.EN_ATENCION

    en_atencion_guardada.cerrar()
    repo_db.actualizar(en_atencion_guardada)

    cerrada = repo_db.buscar_por_solicitud_id("sol-004")
    assert cerrada is not None
    assert cerrada.estado == EstadoAtencion.CERRADA
