"""Gestor en memoria: maneja las listas internas de clientes, servicios y reservas."""
from cliente import Cliente
from excepciones import ErrorSoftwareFJ, ParametroFaltanteError, ServicioInvalidoError
from logger import obtener_logger
from reserva import Reserva
from servicios import Asesoria, AlquilerEquipo, ReservaSala

log = obtener_logger("gestor")


class GestorFJ:
    """Centraliza el registro de objetos. Nunca deja que un error detenga el programa."""

    TIPOS = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": Asesoria}

    def __init__(self):
        self.clientes = []  # lista interna de clientes
        self.servicios = []  # lista interna de servicios
        self.reservas = []  # lista interna de reservas

    def registrar_cliente(self, **datos):
        try:
            cliente = Cliente(**datos)
        except TypeError as e:  # faltan o sobran argumentos
            err = ParametroFaltanteError(f"Parámetros de cliente incorrectos: {e}")
            log.error("%s", err)
            return None
        except ErrorSoftwareFJ:  # ya fue registrado en el log por Cliente
            return None
        self.clientes.append(cliente)
        return cliente

    def crear_servicio(self, tipo, **datos):
        try:
            if tipo not in self.TIPOS:
                raise ServicioInvalidoError(f"Tipo de servicio desconocido: {tipo!r}.")
            try:
                servicio = self.TIPOS[tipo](**datos)
            except TypeError as e:  # faltan parámetros obligatorios
                raise ParametroFaltanteError(f"Faltan parámetros para '{tipo}': {e}") from e
        except ErrorSoftwareFJ as e:
            log.error("Servicio no creado: %s", e)
            return None
        self.servicios.append(servicio)
        log.info("Servicio creado: %s", servicio.describir())
        return servicio

    def crear_reserva(self, cliente, servicio, horas):
        try:
            reserva = Reserva(cliente, servicio, horas)
        except ErrorSoftwareFJ as e:
            log.error("Reserva no creada: %s", e)
            return None
        self.reservas.append(reserva)
        return reserva
