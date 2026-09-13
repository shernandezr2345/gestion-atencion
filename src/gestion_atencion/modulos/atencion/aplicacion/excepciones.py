"""Excepciones de la capa de aplicación de gestión de atención."""


class ErrorAplicacionAtencion(Exception):
    """Excepción base para errores de la capa de aplicación."""


class AtencionNoEncontradaError(ErrorAplicacionAtencion):
    """Se lanza cuando no existe una atención para el identificador solicitado."""


class AtencionYaExisteError(ErrorAplicacionAtencion):
    """Se lanza cuando ya existe una atención para la misma solicitud."""
