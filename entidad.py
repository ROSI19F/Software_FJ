"""Clase abstracta base para todas las entidades del sistema."""
from abc import ABC, abstractmethod  # herramientas para clases abstractas


class Entidad(ABC):
    """Representa cualquier entidad general (Cliente, Servicio, Reserva)."""

    _contadores = {}  # contador de ids por tipo de entidad

    def __init__(self):
        base = next(c for c in type(self).__mro__ if c.__bases__ == (Entidad,))  # Cliente, Servicio o Reserva
        Entidad._contadores[base] = Entidad._contadores.get(base, 0) + 1  # incrementa su contador
        self._id = Entidad._contadores[base]  # asigna el id (encapsulado)

    @property
    def id(self):
        """Identificador de solo lectura."""
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe devolver una descripción en texto (polimorfismo)."""

    def __str__(self):
        return self.describir()  # str(objeto) usa la descripción propia de cada clase
