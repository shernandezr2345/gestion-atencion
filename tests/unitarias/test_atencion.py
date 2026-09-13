import pytest

from gestion_atencion.modulos.atencion.dominio.entidades import Atencion
from gestion_atencion.modulos.atencion.dominio.objetos_valor import (
    EstadoAtencion,
    PartnerId,
    ReferenciaExterna,
    SolicitudId,
    TipoServicio,
)
from gestion_atencion.modulos.atencion.dominio.excepciones import EstadoTransicionInvalidaError


def _crear_atencion() -> Atencion:
    return Atencion.crear(
        solicitud_id=SolicitudId("sol-123"),
        partner_id=PartnerId("partner-456"),
        referencia_externa=ReferenciaExterna("REF-001"),
        tipo_servicio=TipoServicio("INSTALACION"),
    )


def test_crear_atencion() -> None:
    atencion = _crear_atencion()
    assert atencion.id_atencion
    assert atencion.solicitud_id == SolicitudId("sol-123")
    assert atencion.estado == EstadoAtencion.PENDIENTE


def test_nueva_atencion_queda_en_pendiente() -> None:
    atencion = _crear_atencion()
    assert atencion.estado == EstadoAtencion.PENDIENTE


def test_pendiente_puede_pasara_en_atencion() -> None:
    atencion = _crear_atencion()
    atencion.cambiar_estado_a_en_atencion()
    assert atencion.estado == EstadoAtencion.EN_ATENCION


def test_en_atencion_puede_pasara_cerrada() -> None:
    atencion = _crear_atencion()
    atencion.cambiar_estado_a_en_atencion()
    atencion.cerrar()
    assert atencion.estado == EstadoAtencion.CERRADA


def test_pendiente_no_puede_pasara_cerrada_directamente() -> None:
    atencion = _crear_atencion()
    with pytest.raises(EstadoTransicionInvalidaError):
        atencion.cerrar()


def test_atencion_cerrada_no_se_puede_modificar() -> None:
    atencion = _crear_atencion()
    atencion.cambiar_estado_a_en_atencion()
    atencion.cerrar()

    with pytest.raises(EstadoTransicionInvalidaError):
        atencion.cambiar_estado_a_en_atencion()


def test_solicitud_id_permanece_inmutable() -> None:
    atencion = _crear_atencion()
    with pytest.raises(AttributeError):
        atencion.solicitud_id = SolicitudId("otra-sol")


def test_estado_invalido_no_puede_existir() -> None:
    with pytest.raises(ValueError):
        EstadoAtencion("INDETERMINADO")


def test_puede_cambiar_estado_a_considera_transiciones_validas() -> None:
    atencion = _crear_atencion()
    assert atencion.puede_cambiar_estado_a(EstadoAtencion.EN_ATENCION) is True
    assert atencion.puede_cambiar_estado_a(EstadoAtencion.CERRADA) is False

    atencion.cambiar_estado_a_en_atencion()
    assert atencion.puede_cambiar_estado_a(EstadoAtencion.CERRADA) is True
    assert atencion.puede_cambiar_estado_a(EstadoAtencion.EN_ATENCION) is False
