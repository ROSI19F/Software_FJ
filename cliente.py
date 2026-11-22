"""Clase Cliente con datos personales encapsulados y validaciones estrictas."""
import re  # expresiones regulares para validar formatos

from entidad import Entidad
from excepciones import ClienteInvalidoError
from logger import obtener_logger

log = obtener_logger("cliente")


class Cliente(Entidad):
    """Cliente de Software FJ. Los datos son privados y se validan en los setters."""

    def __init__(self, nombre, documento, correo, telefono):
        super().__init__()  # genera el id
        try:
            self.nombre = nombre  # pasa por el setter (valida)
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
        except ClienteInvalidoError as e:
            log.error("Cliente no creado: %s", e)  # registra el error
            raise  # lo relanza para que el llamador decida
        else:
            log.info("Cliente creado: %s (doc %s)", self._nombre, self._documento)

    # ---- nombre ----
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):  # debe ser texto
            raise ClienteInvalidoError("El nombre debe ser texto.")
        valor = valor.strip()  # quita espacios sobrantes
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}", valor):  # solo letras, 3 a 60
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'.")
        self._nombre = valor

    # ---- documento ----
    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip() if valor is not None else ""
        if not re.fullmatch(r"\d{6,12}", valor):  # solo dígitos, 6 a 12
            raise ClienteInvalidoError(f"Documento inválido: '{valor}'.")
        self._documento = valor

    # ---- correo ----
    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", valor.strip()):
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    # ---- teléfono ----
    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip() if valor is not None else ""
        if not re.fullmatch(r"\d{7,10}", valor):  # 7 a 10 dígitos
            raise ClienteInvalidoError(f"Teléfono inválido: '{valor}'.")
        self._telefono = valor

    def describir(self):
        return f"Cliente #{self.id}: {self._nombre} | Doc: {self._documento} | {self._correo}"
