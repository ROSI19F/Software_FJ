"""Excepciones personalizadas del sistema Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Excepción base: todas las demás heredan de ella para poder capturarlas juntas."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los datos de un cliente no pasan las validaciones."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio se crea con datos o tipo incorrectos."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta usar un servicio marcado como no disponible."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza cuando una reserva es incorrecta o no se puede procesar."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se lanza cuando se pide una operación que el estado actual no permite."""


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando un cálculo de costos produce o recibe valores absurdos."""


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se lanza cuando faltan parámetros obligatorios al crear un objeto."""
