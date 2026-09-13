from gestion_atencion.modulos.atencion.infraestructura.schema.v1.eventos import (
    EventoSolicitudPartnerRegistradaV1,
    EventoSolicitudPartnerRegistradaV2,
    SolicitudPartnerRegistradaPayloadV1,
    SolicitudPartnerRegistradaPayloadV2,
)
from gestion_atencion.seedwork.infraestructura.schema.v1.mensajes import Mensaje


def _campos_payload(payload_cls):
    return {campo: getattr(payload_cls, campo) for campo in payload_cls.__annotations__}


def test_schema_v1_existe_y_es_valido():
    assert issubclass(EventoSolicitudPartnerRegistradaV1, Mensaje)
    assert EventoSolicitudPartnerRegistradaV1.event_type == "SolicitudPartnerRegistrada"
    assert EventoSolicitudPartnerRegistradaV1.event_version == "v1"

    payload = _campos_payload(SolicitudPartnerRegistradaPayloadV1)
    assert set(payload) == {
        "solicitud_id",
        "partner_id",
        "referencia_externa",
        "tipo_servicio",
    }


def test_schema_v2_existe_y_es_compatible_con_v1_y_agrega_estado():
    assert issubclass(EventoSolicitudPartnerRegistradaV2, Mensaje)
    assert EventoSolicitudPartnerRegistradaV2.event_type == "SolicitudPartnerRegistrada"
    assert EventoSolicitudPartnerRegistradaV2.event_version == "v2"

    payload_v1 = _campos_payload(SolicitudPartnerRegistradaPayloadV1)
    payload_v2 = _campos_payload(SolicitudPartnerRegistradaPayloadV2)

    assert set(payload_v1).issubset(set(payload_v2))
    assert set(payload_v2) - set(payload_v1) == {"estado"}
    assert payload_v2["estado"] == "" or payload_v2["estado"] is None
