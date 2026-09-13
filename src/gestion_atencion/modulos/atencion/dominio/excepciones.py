"""Excepciones del dominio de Gestión de Atención."""


class ErrorDominioAtencion(Exception):
    """Base para errores del dominio."""


class ValueObjectInvalidoError(ErrorDominioAtencion):
    """Se lanza cuando un Value Object no cumple sus invariantes."""


class EstadoTransicionInvalidaError(ErrorDominioAtencion):
    """Se lanza cuando se intenta una transición no permitida."""
