"""Simulación de 15 operaciones de Software FJ (válidas e inválidas) sin base de datos."""
from excepciones import ErrorSoftwareFJ
from gestor import GestorFJ
from logger import RUTA_LOG, obtener_logger

log = obtener_logger("main")


def ejecutar(numero, titulo, accion):
    """Ejecuta una operación; si falla, muestra el error y el programa continúa."""
    print(f"\n[{numero:02d}] {titulo}")
    try:
        resultado = accion()
    except ErrorSoftwareFJ as e:  # errores controlados del sistema
        causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
        print(f"     ERROR CONTROLADO: {type(e).__name__}: {e}{causa}")
        log.error("Operación %s falló: %s", numero, e)
        return None
    except Exception as e:  # cualquier error inesperado tampoco detiene el sistema
        print(f"     ERROR INESPERADO: {type(e).__name__}: {e}")
        log.critical("Operación %s error inesperado: %r", numero, e)
        return None
    else:
        if resultado in ("rechazado", "rechazada"):  # el gestor rechazó el dato y lo registró en el log
            print("     RECHAZADO CONTROLADAMENTE (ver log)")
            log.warning("Operación %s rechazada", numero)
        else:
            print(f"     OK: {resultado}")
            log.info("Operación %s exitosa", numero)
        return resultado
    finally:
        log.debug("Operación %s finalizada", numero)


def main():
    g = GestorFJ()
    log.info("===== INICIO DE LA SIMULACIÓN =====")

    # ----- Clientes -----
    ana = ejecutar(1, "Registro VÁLIDO de cliente", lambda: g.registrar_cliente(
        nombre="Ana Torres", documento="1020304050", correo="ana@correo.com", telefono="3001234567") or "rechazado")
    ejecutar(2, "Registro INVÁLIDO de cliente (correo mal formado)", lambda: g.registrar_cliente(
        nombre="Pedro Gómez", documento="123456789", correo="pedro-sin-arroba", telefono="3001112233") or "rechazado")
    ejecutar(3, "Registro INVÁLIDO de cliente (parámetro faltante)", lambda: g.registrar_cliente(
        nombre="Luis Pérez", documento="987654321") or "rechazado")
    carlos = ejecutar(4, "Registro VÁLIDO de cliente", lambda: g.registrar_cliente(
        nombre="Carlos Ruiz", documento="79845612", correo="carlos@correo.com", telefono="3109876543") or "rechazado")

    # ----- Servicios -----
    sala = ejecutar(5, "Creación VÁLIDA de sala", lambda: g.crear_servicio(
        "sala", nombre="Sala Ejecutiva", tarifa_hora=50000, capacidad=25) or "rechazado")
    equipo = ejecutar(6, "Creación VÁLIDA de alquiler de equipo", lambda: g.crear_servicio(
        "equipo", nombre="Alquiler Portátiles", tarifa_hora=8000, equipo="Portátil", cantidad=3) or "rechazado")
    asesoria = ejecutar(7, "Creación VÁLIDA de asesoría", lambda: g.crear_servicio(
        "asesoria", nombre="Asesoría Cloud", tarifa_hora=70000, especialidad="Cloud", nivel="senior") or "rechazado")
    ejecutar(8, "Creación INVÁLIDA de servicio (tarifa negativa)", lambda: g.crear_servicio(
        "sala", nombre="Sala Rota", tarifa_hora=-100, capacidad=10) or "rechazado")
    ejecutar(9, "Creación INVÁLIDA de servicio (falta 'capacidad')", lambda: g.crear_servicio(
        "sala", nombre="Sala Incompleta", tarifa_hora=40000) or "rechazado")

    # ----- Reservas -----
    r1 = g.crear_reserva(ana, sala, 3)  # objeto reserva válida
    def flujo_exitoso():
        r1.confirmar()  # PENDIENTE -> CONFIRMADA
        r1.procesar(0.19, 0.10)  # costo con IVA y 10 % de descuento
        return r1
    ejecutar(10, "Reserva EXITOSA (confirmar + procesar con descuento)", flujo_exitoso)

    r2 = g.crear_reserva(carlos, sala, 20)  # 20 h supera el máximo de 8
    ejecutar(11, "Reserva FALLIDA (duración fuera de rango)", lambda: r2.confirmar())

    equipo.disponible = False  # simulamos que el servicio dejó de estar disponible
    r3 = g.crear_reserva(carlos, equipo, 5)
    ejecutar(12, "Reserva FALLIDA (servicio no disponible)", lambda: r3.confirmar())
    equipo.disponible = True

    r4 = g.crear_reserva(ana, asesoria, 2)
    def cancelar_y_confirmar():
        r4.cancelar()
        r4.confirmar()  # no permitido: ya está cancelada
    ejecutar(13, "Operación NO PERMITIDA (confirmar reserva cancelada)", cancelar_y_confirmar)

    r5 = g.crear_reserva(carlos, asesoria, 1.5)
    def calculo_inconsistente():
        r5.confirmar()
        r5.procesar(0.19, 1.5)  # descuento del 150 %: inconsistente
    ejecutar(14, "CÁLCULO INCONSISTENTE (excepción encadenada)", calculo_inconsistente)

    ejecutar(15, "Reserva INVÁLIDA (cliente None)", lambda: g.crear_reserva(None, sala, 2) or "rechazada")

    # ----- Resumen -----
    print("\n=== RESUMEN FINAL ===")
    for r in g.reservas:
        print(" ", r)
    print(f"\nEl programa terminó sin interrupciones. Revise el log en: {RUTA_LOG}")
    log.info("===== FIN DE LA SIMULACIÓN =====")


if __name__ == "__main__":
    main()
