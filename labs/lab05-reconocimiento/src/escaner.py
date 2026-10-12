#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
escaner.py — Ampliación OPCIONAL del Lab 05.

nmap es magia hasta que entendés qué hace por dentro. Y lo que hace un escaneo
TCP "connect" es simple: intentar abrir una conexión a cada puerto y ver si el
otro lado contesta. Nada más. Acá lo implementás vos, con la biblioteca estándar.

Cuando termines, vas a mirar la salida de nmap con otros ojos: vas a SABER qué
significa "open", "closed" y "filtered", porque los produjiste vos.

Uso previsto (desde la consola del atacante, con el lab levantado):

    python3 escaner.py phantomcorp --puertos 1-1000
    python3 escaner.py phantomcorp --puertos 21,80,8080,31337 --banner

Esto NO reemplaza a nmap para el informe. Es para entender. El recon del
entregable se hace con nmap.

Solo biblioteca estándar. No modifiques la interfaz de la CLI.
"""
import argparse
import socket
import sys

# ── Referencia YA implementada: leela antes de tocar nada. ───────────────────
def probar_puerto(host: str, puerto: int, timeout: float = 0.5) -> bool:
    """Devuelve True si el puerto TCP está ABIERTO (aceptó la conexión).

    Este es el corazón de un escaneo 'connect': un socket, un connect con
    timeout, y la respuesta del sistema operativo. Si connect_ex devuelve 0,
    hubo three-way handshake completo → puerto abierto.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, puerto)) == 0


# ── B.1 — Parsear el rango de puertos. TODO ─────────────────────────────────
def parsear_puertos(spec: str) -> list[int]:
    """Convierte '21,80,8080' o '1-1000' (o mezcla) en una lista de ints.

    Ejemplos:
        '21,80,8080'  -> [21, 80, 8080]
        '1-3'         -> [1, 2, 3]
        '80,100-102'  -> [80, 100, 101, 102]

    Requisitos:
      - Aceptar puertos sueltos separados por coma y rangos con guion.
      - Validar que estén en 1..65535; si no, error claro y salir con código 2.
      - Sin duplicados y ordenados.
    """
    # TODO: implementá esto.
    raise NotImplementedError("Completá parsear_puertos()")


# ── B.2 — Banner grabbing. TODO ──────────────────────────────────────────────
def leer_banner(host: str, puerto: int, timeout: float = 1.0) -> str:
    """Conecta al puerto y devuelve hasta 256 bytes que el servicio envíe.

    Pista: no todos los servicios saludan solos. Un servidor HTTP no dice nada
    hasta que le mandás algo. Un FTP sí saluda. Con implementar el caso 'el
    servicio habla primero' alcanza para este lab (FTP en 21, el de 31337).

    Devolvé el texto decodificado (errors='replace') y sin espacios al borde.
    Si no llega nada, devolvé cadena vacía.
    """
    # TODO: implementá esto.
    raise NotImplementedError("Completá leer_banner()")


def main() -> int:
    ap = argparse.ArgumentParser(description="Mini escáner TCP connect (Lab 05).")
    ap.add_argument("host", help="host o IP objetivo (ej: phantomcorp)")
    ap.add_argument("--puertos", default="1-1024",
                    help="lista/rango de puertos. Ej: 21,80 o 1-1000")
    ap.add_argument("--banner", action="store_true",
                    help="intentar leer el banner de cada puerto abierto")
    ap.add_argument("--timeout", type=float, default=0.5)
    args = ap.parse_args()

    puertos = parsear_puertos(args.puertos)
    print(f"[*] Escaneando {args.host} — {len(puertos)} puertos...")
    abiertos = []
    for p in puertos:
        if probar_puerto(args.host, p, args.timeout):
            abiertos.append(p)
            linea = f"  {p:>5}/tcp  ABIERTO"
            if args.banner:
                b = leer_banner(args.host, p)
                if b:
                    linea += f"   banner: {b!r}"
            print(linea)
    print(f"[*] Listo. {len(abiertos)} puerto(s) abierto(s): {abiertos}")
    # Código de salida: 0 si no se encontró nada abierto, 1 si sí (útil en scripts).
    return 1 if abiertos else 0


if __name__ == "__main__":
    sys.exit(main())
