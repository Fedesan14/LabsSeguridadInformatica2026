#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
timeline.py — Ampliación del Lab 11. Reconstruí la línea de tiempo del ataque
automáticamente, en vez de leer el log a ojo. Solo biblioteca estándar.

Analizar a mano 20 líneas se puede; analizar 200.000 no. Por eso el forense
scriptea. Completá los TODO y corré:

    python3 timeline.py ../caso/logs/access.log --ip 185.220.101.42

La función parsear_linea() viene YA implementada como referencia: leela, es la
base de todo.
"""
import argparse
import re
import sys

# Formato nginx combined:  IP - - [fecha] "METODO ruta HTTP/x" status ...
LOG_RE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) [^"]*" (\d{3})')

def parsear_linea(linea: str):
    """Devuelve {ip, ts, metodo, ruta, status} o None si la línea no matchea
    (comentarios, tráfico raro). YA IMPLEMENTADA."""
    m = LOG_RE.match(linea)
    if not m:
        return None
    ip, ts, metodo, ruta, status = m.groups()
    return {"ip": ip, "ts": ts, "metodo": metodo, "ruta": ruta, "status": int(status)}


def construir_timeline(path: str, ip: str = None) -> list:
    """Recorre el log, parsea cada línea y devuelve la lista de eventos.
    Si `ip` no es None, filtrá SOLO los eventos de esa IP (la del atacante).

    TODO:
      - abrí el archivo y parseá cada línea con parsear_linea().
      - descartá las que devuelven None.
      - si `ip` fue pasada, quedate solo con las de esa IP.
      - el log ya viene en orden cronológico; no hace falta reordenar.
    """
    # TODO: implementá esto.
    raise NotImplementedError("Completá construir_timeline()")


def clasificar_fase(ruta: str) -> str:
    """Mapea una petición a la fase del ataque, para etiquetar la timeline.
    Devolvé una etiqueta corta: RECON · ENUM · EXPLOIT · RCE · WEBSHELL · EXFIL.

    TODO: mirá las rutas del caso (login, /api/reporte?cmd=, shell.php,
    clientes...) y devolvé la fase que corresponde. Pista: usá 'in' sobre la ruta.
    """
    # TODO: implementá esto.
    raise NotImplementedError("Completá clasificar_fase()")


def main() -> int:
    ap = argparse.ArgumentParser(description="Timeline forense de un access.log.")
    ap.add_argument("log")
    ap.add_argument("--ip", default=None, help="filtrar por la IP del atacante")
    a = ap.parse_args()
    eventos = construir_timeline(a.log, a.ip)
    print(f"[*] {len(eventos)} eventos" + (f" de {a.ip}" if a.ip else ""))
    for e in eventos:
        print(f"  {e['ts']}  {e['metodo']:4s} {e['ruta']:40s} [{clasificar_fase(e['ruta'])}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
