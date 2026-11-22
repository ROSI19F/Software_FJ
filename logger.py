"""Configuración del archivo de logs (único uso de archivos permitido por el enunciado)."""
import logging  # módulo estándar de registro de eventos
import os  # para construir rutas y crear carpetas

# Ruta del archivo de logs: carpeta "logs" junto a este archivo
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "software_fj.log")

# Logger raíz de la aplicación; los demás módulos usan hijos de este
_raiz = logging.getLogger("softwarefj")

if not _raiz.handlers:  # evita duplicar handlers si el módulo se importa varias veces
    os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)  # crea la carpeta si no existe
    _handler = logging.FileHandler(RUTA_LOG, encoding="utf-8")  # escribe en el archivo
    _handler.setFormatter(  # formato: fecha | nivel | módulo | mensaje
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    _raiz.addHandler(_handler)  # activa el handler
    _raiz.setLevel(logging.DEBUG)  # registra todos los niveles
    _raiz.propagate = False  # no imprime en consola, solo en archivo


def obtener_logger(nombre):
    """Devuelve un logger hijo identificado con el nombre del módulo que lo pide."""
    return logging.getLogger(f"softwarefj.{nombre}")
