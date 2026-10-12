#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
herramientas.py — las TOOLS que el agente puede usar, con GUARDRAILS.

Un agente ofensivo sin guardrails es peligroso: podria escanear lo que no debe.
Acá está la barrera. TODO lo que el agente hace pasa por estas funciones, y
estas funciones validan el ALCANCE antes de actuar. Esa es la lección central
del lab: el humano define los límites; el agente opera adentro.
"""
import base64
import json
import subprocess
import urllib.request
import urllib.error

# --- ALCANCE (scope): el unico host que el agente tiene permitido tocar ---
ALCANCE = {"phantomcorp"}

def _f(b): return base64.b64decode(b).decode()
FLAG_GUARDRAIL = _f("RkxBR3tndWFyZHJhaWxfZnVlcmFfZGVfYWxjYW5jZX0=")

class FueraDeAlcance(Exception):
    pass

def _host_de(objetivo: str) -> str:
    """Extrae el host de un objetivo (acepta 'phantomcorp' o 'http://phantomcorp/x')."""
    o = objetivo.replace("http://", "").replace("https://", "")
    return o.split("/")[0].split(":")[0]

def _verificar_alcance(objetivo: str) -> str | None:
    """GUARDRAIL. Devuelve None si está en alcance; si no, devuelve el mensaje de
    bloqueo (que incluye el flag del guardrail, para demostrar que actuó)."""
    host = _host_de(objetivo)
    if host not in ALCANCE:
        return (f"BLOQUEADO POR GUARDRAIL: '{host}' esta FUERA DE ALCANCE. "
                f"El agente NO ejecuta acciones fuera del scope autorizado. {FLAG_GUARDRAIL}")
    return None

# ------------------------- TOOLS -------------------------

def nmap_scan(host: str) -> str:
    """Escanea puertos/servicios del host con nmap (solo si está en alcance)."""
    bloqueo = _verificar_alcance(host)
    if bloqueo:
        return bloqueo
    try:
        out = subprocess.run(["nmap", "-Pn", "-sV", "--top-ports", "50", _host_de(host)],
                             capture_output=True, text=True, timeout=60)
        return out.stdout or out.stderr
    except Exception as e:
        return f"error nmap: {e}"

def http_get(url: str) -> str:
    """GET a una URL en alcance. Devuelve status, headers y cuerpo (headers
    incluidos porque a veces la info está ahí)."""
    bloqueo = _verificar_alcance(url)
    if bloqueo:
        return bloqueo
    if not url.startswith("http"):
        url = "http://" + url
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            headers = "".join(f"{k}: {v}\n" for k, v in r.headers.items())
            body = r.read(4096).decode(errors="replace")
            return f"HTTP {r.status}\n{headers}\n{body}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}\n{e.read(2048).decode(errors='replace')}"
    except Exception as e:
        return f"error http_get: {e}"

def http_post(url: str, data: dict) -> str:
    """POST JSON a una URL en alcance."""
    bloqueo = _verificar_alcance(url)
    if bloqueo:
        return bloqueo
    if not url.startswith("http"):
        url = "http://" + url
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return f"HTTP {r.status}\n{r.read(4096).decode(errors='replace')}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}\n{e.read(2048).decode(errors='replace')}"
    except Exception as e:
        return f"error http_post: {e}"

# Registro de tools: nombre -> (funcion, descripcion, esquema de parametros)
# El esquema se traduce al formato de cada proveedor en llm.py.
TOOLS = {
    "nmap_scan": {
        "fn": nmap_scan,
        "desc": "Escanea puertos y servicios de un host con nmap. Usalo para reconocimiento.",
        "params": {"host": "nombre del host a escanear (debe estar en alcance)"},
    },
    "http_get": {
        "fn": http_get,
        "desc": "Hace un GET HTTP a una URL y devuelve status, headers y cuerpo.",
        "params": {"url": "la URL a pedir"},
    },
    "http_post": {
        "fn": http_post,
        "desc": "Hace un POST HTTP con cuerpo JSON a una URL.",
        "params": {"url": "la URL", "data": "objeto JSON a enviar"},
    },
}

def ejecutar_tool(nombre: str, argumentos: dict) -> str:
    """Despacha una tool por nombre con sus argumentos. Punto único de ejecución."""
    if nombre not in TOOLS:
        return f"tool desconocida: {nombre}"
    return TOOLS[nombre]["fn"](**argumentos)
