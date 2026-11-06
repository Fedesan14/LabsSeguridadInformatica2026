"""Orquestador: el único componente que valida, registra y ejecuta.

Loop secuencial hasta un punto fijo (ningún agente propone nada nuevo) o hasta
`max_pasos`. Secuencial a propósito: el orden de ejecución es parte del
resultado, y en serie el orden lo fija la lista de agentes, no el scheduler.

`ejecutar` se inyecta: en la demo es el sandbox Docker y en el test un falso
con salidas fijas, así el swarm entero se prueba sin red ni contenedores.
"""
import os
import sys
from dataclasses import asdict

from agentes import AgenteEnum, AgenteRecon, hallazgos_http
from bitacora import Bitacora
from roe import validar


def correr(agentes, bitacora, ejecutar, max_pasos=200):
    pizarra, hechas = {}, set()
    for paso in range(1, max_pasos + 1):
        pendientes = [(ag, a) for ag in agentes for a in ag.proponer(pizarra) if a not in hechas]
        if not pendientes:
            break
        ag, accion = pendientes[0]
        # Se marca antes de validar: una acción rechazada no se vuelve a proponer.
        hechas.add(accion)
        try:
            argv = validar(accion)
        except PermissionError as e:
            bitacora.registrar(paso, ag.nombre, "rechazada", {"accion": asdict(accion), "motivo": str(e)})
            continue
        bitacora.registrar(paso, ag.nombre, "propuesta", {"argv": argv})
        try:
            rc, salida = ejecutar(argv)
        except OSError as e:
            bitacora.registrar(paso, ag.nombre, "error", {"motivo": str(e)})
            raise
        bitacora.registrar(paso, ag.nombre, "resultado", {"rc": rc, "salida": salida})
        ag.interpretar(accion, salida, pizarra)
    return pizarra


if __name__ == "__main__":
    from sandbox import ejecutar_docker

    clave = os.environ.get("PTAAS_CLAVE", "").encode()
    if not clave:
        sys.exit("definí PTAAS_CLAVE: es la clave HMAC de la bitácora")
    bitacora = Bitacora(sys.argv[1] if len(sys.argv) > 1 else "bitacora.jsonl", clave)
    pizarra = correr([AgenteRecon(), AgenteEnum()], bitacora, ejecutar_docker)
    print("puertos:", pizarra.get("puertos"))
    print("rutas:", hallazgos_http(pizarra))
    print("cabeza de la bitácora:", bitacora.ultimo)
