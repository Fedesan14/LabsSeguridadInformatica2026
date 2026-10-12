#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
verificar-defensa.py — Lab Extra 3 (hardening). El "atacante del docente".

  python3 verificar-defensa.py [--dir <carpeta con tu server.py parchado>]

Levanta la app del --dir indicado en un puerto local, la ATACA con las cinco
técnicas de los labs 05-07 y verifica qué defensas quedaron bien. Por cada
ataque bloqueado, te da la flag para entregar:

  ./ctf submit extra3 D1 'FLAG{...}'

Verde = ataque bloqueado (bien). Rojo = todavía vulnerable.
"""
import argparse
import base64
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

OK, NO, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

def _f(b64: str) -> str:
    return base64.b64decode(b64).decode()

# Las flags se GANAN bloqueando el ataque, no leyendo esto.
FLAGS = {
    "D1": _f("RkxBR3tkZWZfYmFubmVyX25ldXRyYWxpemFkb30="),
    "D2": _f("RkxBR3tkZWZfZGVidWdfYXBhZ2Fkb30="),
    "D3": _f("RkxBR3tkZWZfcnV0YXNfYmxpbmRhZGFzfQ=="),
    "D4": _f("RkxBR3tkZWZfc3FsaV9wYXJhbWV0cml6YWRvfQ=="),
    "D5": _f("RkxBR3tkZWZfdHJhdmVyc2FsX2Jsb3F1ZWFkb30="),
}

BASE = "http://127.0.0.1:{port}"


def get(port, path, timeout=4):
    """Devuelve (status, headers, cuerpo-decodificado) o (0, {}, error)."""
    try:
        req = urllib.request.Request(BASE.format(port=port) + path)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(8192).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(8192).decode("utf-8", "ignore")
    except Exception as e:
        return 0, {}, str(e)


def ataques(port):
    """Cada función devuelve True si la DEFENSA está bien (ataque bloqueado)."""
    resultados = {}

    # D1 — banner: el header Server no debe cantar producto+versión
    _, h, _ = get(port, "/")
    server = h.get("Server", "")
    resultados["D1"] = ("PhantomServer" not in server and "2.4.1" not in server), \
        f"header Server: {server!r}"

    # D2 — debug: /api/status no debe existir o no debe exponer debug/pid/rutas
    s, _, cuerpo = get(port, "/api/status")
    expone = '"debug"' in cuerpo or '"pid"' in cuerpo or "/tmp/" in cuerpo
    resultados["D2"] = (s == 404 or (s in (401, 403)) or not expone), \
        f"GET /api/status -> {s} {cuerpo[:60]!r}"

    # D3 — rutas: /backup no debe responder 200 sin auth; robots no debe delatarla
    s1, _, c1 = get(port, "/backup")
    _, _, robots = get(port, "/robots.txt")
    resultados["D3"] = (s1 in (401, 403, 404)) and ("/backup" not in robots), \
        f"GET /backup -> {s1}; robots menciona /backup: {'/backup' in robots}"

    # D4 — SQLi: los bypass clásicos no deben loguear (params URL-encoded)
    from urllib.parse import quote
    inj1 = "/login?user=" + quote("admin'--") + "&pass=x"
    inj2 = "/login?user=x&pass=" + quote("' OR 1=1 --")
    s, _, cuerpo = get(port, inj1)
    s2, _, cuerpo2 = get(port, inj2)
    bypass = ("Bienvenido" in cuerpo) or ("Bienvenido" in cuerpo2)
    resultados["D4"] = not bypass, \
        f"bypass admin'--: {'FUNCIONA (vulnerable)' if 'Bienvenido' in cuerpo else 'bloqueado'}; " \
        f"OR 1=1: {'FUNCIONA (vulnerable)' if 'Bienvenido' in cuerpo2 else 'bloqueado'}"

    # D5 — traversal: ../../etc/passwd no debe volver
    s, _, cuerpo = get(port, "/descargar?archivo=../../../../etc/passwd")
    resultados["D5"] = ("root:" not in cuerpo), \
        f"traversal /etc/passwd -> {s} ({'FILTRADO (vulnerable)' if 'root:' in cuerpo else 'bloqueado'})"

    return resultados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None,
                    help="carpeta con el server.py a probar (default: el objetivo vulnerable del lab)")
    ap.add_argument("--port", type=int, default=18341)
    args = ap.parse_args()

    aqui = os.path.dirname(os.path.abspath(__file__))
    directorio = args.dir or os.path.join(aqui, "objetivo")
    server = os.path.join(directorio, "server.py")
    if not os.path.exists(server):
        sys.exit(f"No encuentro {server}. Pasá --dir <tu copia parchada>.")

    print(f"\n== Lab Extra 3 · verificación de defensas ==")
    print(f"{DIM}Objetivo bajo prueba: {server}{RST}\n")

    proc = subprocess.Popen(
        [sys.executable, server],
        env={**os.environ, "PORT": str(args.port)},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.2)
        resultados = ataques(args.port)
    finally:
        proc.terminate()

    bloqueadas = 0
    for did, (bloqueado, detalle) in resultados.items():
        if bloqueado:
            bloqueadas += 1
            print(f"  {OK}✓{RST} {did} — ataque BLOQUEADO  {DIM}({detalle}){RST}")
            print(f"      flag: {FLAGS[did]}")
        else:
            print(f"  {NO}✗{RST} {did} — todavía vulnerable  {DIM}({detalle}){RST}")
    print(f"\n{OK if bloqueadas == 5 else NO}{bloqueadas}/5 defensas correctas.{RST}")
    if bloqueadas == 5:
        print(f"{OK}Objetivo endurecido. Entregá las 5 flags y escribí el informe.{RST}")
    return 0 if bloqueadas == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
