"""Base de mensajes de integración siguiendo el patrón del tutorial CQRS/Eventos."""

try:
    from pulsar.schema import Long, Record, String
except ModuleNotFoundError:  # pragma: no cover
    class Record:  # type: ignore[override]
        pass

    class String(str):
        def __new__(cls, default=None):
            return str.__new__(cls, default or "")

    class Long(int):
        def __new__(cls, default=None):
            return int.__new__(cls, default or 0)


class Mensaje(Record):
    event_id: str = String()
    event_time: int = Long()
    event_type: str = String()
    event_version: str = String()
