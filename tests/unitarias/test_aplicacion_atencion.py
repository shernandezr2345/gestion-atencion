import pytest

from gestion_atencion.modulos.atencion.aplicacion.excepciones import (
    AtencionNoEncontradaError,
    AtencionYaExisteError,
)
from gestion_atencion.modulos.atencion.aplicacion.servicios import (
    CambiarEstadoAtencion,
    CrearAtencion,
)
from gestion_atencion.modulos.atencion.dominio.entidades import Atencion
from gestion_atencion.modulos.atencion.dominio.excepciones import EstadoTransicionInvalidaError
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)


class FakeRepository:
    def __init__(self, atenciones=None):
        self.atenciones = atenciones or {}

    def buscar_por_solicitud_id(self, solicitud_id):
        return self.atenciones.get(solicitud_id)

    def guardar(self, atencion):
        self.atenciones[atencion.solicitud_id.valor] = atencion

    def actualizar(self, atencion):
        self.atenciones[atencion.solicitud_id.valor] = atencion


def test_crea_una_atencion_cuando_no_existe():
    repo = FakeRepository()
    caso_uso = CrearAtencion(repo)

    resultado = caso_uso.ejecutar(
        solicitud_id="sol-101",
        partner_id="partner-101",
        referencia_externa="REF-101",
        tipo_servicio="INSTALACION",
    )

    assert isinstance(resultado, Atencion)
    assert resultado.solicitud_id == SolicitudId("sol-101")
    assert resultado.partner_id == PartnerId("partner-101")
    assert resultado.referencia_externa == ReferenciaExterna("REF-101")
    assert resultado.tipo_servicio == TipoServicio("INSTALACION")
    assert resultado.estado == EstadoAtencion.PENDIENTE


def test_no_crea_una_segunda_atencion_si_ya_existe():
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-102"),
        partner_id=PartnerId("partner-102"),
        referencia_externa=ReferenciaExterna("REF-102"),
        tipo_servicio=TipoServicio("MANTENIMIENTO"),
    )
    repo = FakeRepository({"sol-102": atencion})
    caso_uso = CrearAtencion(repo)

    with pytest.raises(AtencionYaExisteError):
        caso_uso.ejecutar(
            solicitud_id="sol-102",
            partner_id="partner-102",
            referencia_externa="REF-102",
            tipo_servicio="MANTENIMIENTO",
        )


def test_crear_atencion_usa_correctamente_los_datos_recibidos():
    repo = FakeRepository()
    caso_uso = CrearAtencion(repo)

    resultado = caso_uso.ejecutar(
        solicitud_id="sol-103",
        partner_id="partner-103",
        referencia_externa="REF-103",
        tipo_servicio="REPARACION",
    )

    assert resultado.solicitud_id.valor == "sol-103"
    assert resultado.partner_id.valor == "partner-103"
    assert resultado.referencia_externa.valor == "REF-103"
    assert resultado.tipo_servicio.valor == "REPARACION"


def test_cambia_estado_de_pendiente_a_en_atencion():
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-104"),
        partner_id=PartnerId("partner-104"),
        referencia_externa=ReferenciaExterna("REF-104"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )
    repo = FakeRepository({"sol-104": atencion})
    caso_uso = CambiarEstadoAtencion(repo)

    resultado = caso_uso.ejecutar("sol-104", EstadoAtencion.EN_ATENCION)

    assert resultado.estado == EstadoAtencion.EN_ATENCION
    assert repo.buscar_por_solicitud_id("sol-104").estado == EstadoAtencion.EN_ATENCION


def test_cambia_estado_de_en_atencion_a_cerrada():
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-105"),
        partner_id=PartnerId("partner-105"),
        referencia_externa=ReferenciaExterna("REF-105"),
        tipo_servicio=TipoServicio("MANTENIMIENTO"),
    )
    atencion.cambiar_estado_a_en_atencion()
    repo = FakeRepository({"sol-105": atencion})
    caso_uso = CambiarEstadoAtencion(repo)

    resultado = caso_uso.ejecutar("sol-105", EstadoAtencion.CERRADA)

    assert resultado.estado == EstadoAtencion.CERRADA
    assert repo.buscar_por_solicitud_id("sol-105").estado == EstadoAtencion.CERRADA


def test_propaga_transicion_de_estado_invalida_definida_por_el_dominio():
    atencion = Atencion.crear(
        solicitud_id=SolicitudId("sol-106"),
        partner_id=PartnerId("partner-106"),
        referencia_externa=ReferenciaExterna("REF-106"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )
    repo = FakeRepository({"sol-106": atencion})
    caso_uso = CambiarEstadoAtencion(repo)

    with pytest.raises(EstadoTransicionInvalidaError):
        caso_uso.ejecutar("sol-106", EstadoAtencion.CERRADA)


def test_reporte_atencion_no_encontrada():
    repo = FakeRepository()
    caso_uso = CambiarEstadoAtencion(repo)

    with pytest.raises(AtencionNoEncontradaError):
        caso_uso.ejecutar("sol-107", EstadoAtencion.EN_ATENCION)
