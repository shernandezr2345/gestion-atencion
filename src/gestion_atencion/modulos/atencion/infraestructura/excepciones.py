class DuplicidadAtencionError(Exception):
    """Se lanza cuando se intenta guardar una atención duplicada para la misma solicitud."""


class ErrorPersistenciaAtencion(Exception):
    """Excepción base para errores de infraestructura del repositorio."""
