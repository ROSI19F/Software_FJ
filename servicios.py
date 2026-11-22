"""Clase abstracta Servicio y tres servicios especializados (herencia + polimorfismo)."""
from abc import abstractmethod

from entidad import Entidad
from excepciones import CalculoInconsistenteError, ServicioInvalidoError
from logger import obtener_logger

log = obtener_logger("servicios")


def _es_numero(valor):
    """True si es int/float real (excluye bool, que en Python es subclase de int)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class Servicio(Entidad):
    """Clase abstracta: define qué debe saber hacer cualquier servicio."""

    IVA = 0.19  # impuesto por defecto

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():  # nombre obligatorio
            raise ServicioInvalidoError("El servicio requiere un nombre válido.")
        if not _es_numero(tarifa_hora) or tarifa_hora <= 0:  # tarifa positiva
            raise ServicioInvalidoError(f"Tarifa inválida: {tarifa_hora!r}.")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)
        log.info("Servicio '%s' ahora disponible=%s", self._nombre, self._disponible)

    # ---- métodos abstractos: cada hijo los sobrescribe ----
    @abstractmethod
    def calcular_costo_base(self, horas):
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, horas):
        """Lanza ServicioInvalidoError si la duración no es válida para este servicio."""

    # ---- sobrecarga simulada con parámetros opcionales ----
    def calcular_costo(self, horas, impuesto=None, descuento=0.0):
        """Variantes de uso (sobrecarga):
        calcular_costo(h)                 -> solo IVA por defecto
        calcular_costo(h, 0.05)           -> con impuesto personalizado
        calcular_costo(h, 0.19, 0.10)     -> con impuesto y descuento
        """
        self.validar_parametros(horas)  # cada hijo valida a su manera
        if impuesto is None:
            impuesto = self.IVA  # valor por defecto
        if not _es_numero(impuesto) or not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto inválido: {impuesto!r}.")
        if not _es_numero(descuento) or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(f"Descuento inválido: {descuento!r}.")
        total = self.calcular_costo_base(horas) * (1 - descuento) * (1 + impuesto)
        if total <= 0:  # verificación de consistencia
            raise CalculoInconsistenteError("El costo calculado no es positivo.")
        return round(total, 2)


class ReservaSala(Servicio):
    """Reserva de salas: recargo del 10 % si la capacidad supera 20 personas."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}.")
        self._capacidad = capacidad

    def validar_parametros(self, horas):
        if not _es_numero(horas) or not 1 <= horas <= 8:  # máximo 8 h por sala
            raise ServicioInvalidoError(f"Sala: duración {horas!r} fuera de 1-8 horas.")

    def calcular_costo_base(self, horas):
        base = self._tarifa_hora * horas
        return base * 1.10 if self._capacidad > 20 else base

    def describir(self):
        return f"Sala '{self._nombre}' (capacidad {self._capacidad}) - ${self._tarifa_hora:,.0f}/h"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: tarifa por hora multiplicada por la cantidad."""

    def __init__(self, nombre, tarifa_hora, equipo, cantidad=1, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(equipo, str) or not equipo.strip():
            raise ServicioInvalidoError("Debe indicar el tipo de equipo.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 1:
            raise ServicioInvalidoError(f"Cantidad inválida: {cantidad!r}.")
        self._equipo = equipo.strip()
        self._cantidad = cantidad

    def validar_parametros(self, horas):
        if not _es_numero(horas) or not 1 <= horas <= 72:  # máximo 3 días
            raise ServicioInvalidoError(f"Equipo: duración {horas!r} fuera de 1-72 horas.")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas * self._cantidad

    def describir(self):
        return f"Alquiler de {self._cantidad} x {self._equipo} - ${self._tarifa_hora:,.0f}/h c/u"


class Asesoria(Servicio):
    """Asesoría especializada: el nivel 'senior' cuesta 1.5 veces la tarifa."""

    NIVELES = {"junior": 1.0, "senior": 1.5}  # multiplicador por nivel

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("Debe indicar la especialidad.")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel inválido: {nivel!r}.")
        self._especialidad = especialidad.strip()
        self._nivel = nivel

    def validar_parametros(self, horas):
        if not _es_numero(horas) or not 0.5 <= horas <= 6:  # de 30 min a 6 h
            raise ServicioInvalidoError(f"Asesoría: duración {horas!r} fuera de 0.5-6 horas.")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self):
        return f"Asesoría de {self._especialidad} ({self._nivel}) - ${self._tarifa_hora:,.0f}/h"
