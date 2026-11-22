"""Clase Reserva: integra cliente, servicio, duración y estado."""
from cliente import Cliente
from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError, ErrorSoftwareFJ, OperacionNoPermitidaError,
    ReservaInvalidaError, ServicioNoDisponibleError,
)
from logger import obtener_logger
from servicios import Servicio

log = obtener_logger("reserva")


class Reserva(Entidad):
    """Ciclo de vida: PENDIENTE -> CONFIRMADA -> PROCESADA (o CANCELADA / FALLIDA)."""

    def __init__(self, cliente, servicio, horas):
        super().__init__()
        if not isinstance(cliente, Cliente):  # valida tipos
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = "PENDIENTE"
        self._costo = None  # se llena al procesar
        log.info("Reserva #%s creada (%s -> %s)", self.id, cliente.nombre, servicio.nombre)

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        """Confirma la reserva. Usa try/except/else/finally."""
        try:
            if self._estado != "PENDIENTE":
                raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self._estado}.")
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(f"'{self._servicio.nombre}' no está disponible.")
            self._servicio.validar_parametros(self._horas)  # puede lanzar ServicioInvalidoError
        except ErrorSoftwareFJ as e:
            log.error("Reserva #%s no confirmada: %s", self.id, e)
            raise  # el programa principal decide qué hacer
        else:  # solo si no hubo excepción
            self._estado = "CONFIRMADA"
            log.info("Reserva #%s confirmada", self.id)
        finally:  # siempre se ejecuta
            log.debug("Intento de confirmación de reserva #%s finalizado", self.id)

    def cancelar(self):
        """Cancela la reserva si aún no fue procesada ni cancelada."""
        try:
            if self._estado in ("PROCESADA", "CANCELADA"):
                raise OperacionNoPermitidaError(f"No se puede cancelar una reserva {self._estado}.")
        except OperacionNoPermitidaError as e:
            log.error("Reserva #%s no cancelada: %s", self.id, e)
            raise
        else:
            self._estado = "CANCELADA"
            log.info("Reserva #%s cancelada", self.id)
        finally:
            log.debug("Intento de cancelación de reserva #%s finalizado", self.id)

    def procesar(self, impuesto=None, descuento=0.0):
        """Calcula el costo final. Encadena excepciones con 'raise ... from'."""
        try:
            if self._estado != "CONFIRMADA":
                raise OperacionNoPermitidaError(f"Solo se procesan reservas CONFIRMADAS (actual: {self._estado}).")
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento)
        except CalculoInconsistenteError as e:
            self._estado = "FALLIDA"  # el error de cálculo marca la reserva como fallida
            log.error("Reserva #%s fallida por cálculo: %s", self.id, e)
            raise ReservaInvalidaError(f"No se pudo procesar la reserva #{self.id}.") from e  # encadenamiento
        except ErrorSoftwareFJ as e:
            log.error("Reserva #%s no procesada: %s", self.id, e)
            raise
        else:
            self._costo = costo
            self._estado = "PROCESADA"
            log.info("Reserva #%s procesada. Total: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            log.debug("Intento de procesamiento de reserva #%s finalizado", self.id)

    def describir(self):
        total = f"${self._costo:,.2f}" if self._costo is not None else "sin calcular"
        return (f"Reserva #{self.id} [{self._estado}] {self._cliente.nombre} -> "
                f"{self._servicio.nombre}, {self._horas} h, total: {total}")
