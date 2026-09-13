try:
    from pulsar.schema import Record, String
except ModuleNotFoundError:  # pragma: no cover
    class Record:  # type: ignore[override]
        pass

    class String(str):
        def __new__(cls, default=None):
            return str.__new__(cls, default or "")


from gestion_atencion.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion


class SolicitudPartnerRegistradaPayloadV1(Record):
    solicitud_id: str = String()
    partner_id: str = String()
    referencia_externa: str = String()
    tipo_servicio: str = String()


class SolicitudPartnerRegistradaPayloadV2(Record):
    solicitud_id: str = String()
    partner_id: str = String()
    referencia_externa: str = String()
    tipo_servicio: str = String()
    estado: str = String(default=None)


class EventoSolicitudPartnerRegistradaV1(EventoIntegracion):
    """Evento de integración con la firma mínima de V1."""

    data: SolicitudPartnerRegistradaPayloadV1 = SolicitudPartnerRegistradaPayloadV1()
    event_type: str = String(default="SolicitudPartnerRegistrada")
    event_version: str = String(default="v1")


class EventoSolicitudPartnerRegistradaV2(EventoIntegracion):
    """Evento de integración con la evolución compatible de V2."""

    data: SolicitudPartnerRegistradaPayloadV2 = SolicitudPartnerRegistradaPayloadV2()
    event_type: str = String(default="SolicitudPartnerRegistrada")
    event_version: str = String(default="v2")


EventoSolicitudPartnerRegistrada = EventoSolicitudPartnerRegistradaV1
