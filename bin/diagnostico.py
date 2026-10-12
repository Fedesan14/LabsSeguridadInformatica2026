#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
diagnostico.py — Diagnóstico corto del cruce a ofensiva (clase 05-06).

NO es una nota. Es un espejo: en 5 minutos te dice qué te quedó de los
fundamentos (labs 01-04) y si tu entorno está listo para atacar (lab 05).

Cómo se usa
-----------
1) Copiá la plantilla de respuestas y completala:

       cp docs/diagnostico-respuestas.txt mi-diagnostico.txt
       # editá mi-diagnostico.txt con tus respuestas

2) Corré el diagnóstico:

       python3 bin/diagnostico.py mi-diagnostico.txt

El Bloque A son conceptos (respondés una letra). El Bloque B se contesta
OPERANDO el lab 05 — si no levantaste el entorno, no vas a poder, y ESE es
justamente el diagnóstico. Las respuestas van hasheadas (igual que las flags):
el script sabe si acertaste, pero la respuesta no está en claro acá.

Para el docente: pediles que peguen la línea RESULTADO del final en su entrega.
Con eso ves de un vistazo quién llega al bloque ofensivo y quién necesita
repasar fundamentos primero.
"""
import hashlib
import sys
from pathlib import Path

OK, NO, DIM, AMBER, CY, RST = (
    "\033[32m", "\033[31m", "\033[2m", "\033[33m", "\033[36m", "\033[0m"
)

# sha256( "<id>|<respuesta normalizada>" ) — salado por pregunta para no
# filtrar respuestas repetidas (dos 'b' dan hashes distintos).
CLAVE = {
    "A1": "3c19a9cac6fc9570611d671af60200312bc0f9bab3b52f13d485189bf1acf5a9",
    "A2": "bdf07a64c00915edc65fbc068e80c1cd1d7f71966696ed499ab6e064fc10798e",
    "A3": "48b3d37215625073239afd3ad63e4d378ade758f0706fe62899c3106412d20fb",
    "A4": "aedfec8abf7c681a2c4eeb4b42e1b038ccc9be72d9feaed4a6ff409a56891fd8",
    "A5": "c8095e6a738b8c3f3abd943afd0f685dd5dc23c5c6205da6af9bfa725983b422",
    "A6": "7614234c924c1a6be2453e775114c4b608011fb1c39f586581d1737e04d9c5aa",
    "A7": "8fb6b105612f5a5d544b3a776299f3d1e50f102401fcec30838d3317e9201a33",
    "A8": "fa273bcb60c9f234a17755338e77eb8a7b8e61b6491de394617daa3e5c83fe9e",
    "B1": "03d64d6d1b22d647f210359cd6cf5bdddbc8e935c50ab5b86dad07ccf3621c29",
    "B2": "6a630c0cd0667d4627f8bc5eb925e9a45873a2f7545a00272a1f070d66f721f9",
    "B3": "3e977245700eb04cd40ed2aaac2278550e839bfa1c963eb5c063818f40b6b997",
}

TITULOS = {
    "A1": "CIA — qué propiedad rompe un ransomware",
    "A2": "Efecto avalancha del hash",
    "A3": "Por qué no comparar MACs con ==",
    "A4": "Principio de Kerckhoffs",
    "A5": "Para qué sirve el salt",
    "A6": "Vector oficial TOTP (RFC 6238)",
    "A7": "Fórmula del ALE",
    "A8": "El error de cripto de Adobe 2013",
    "B1": "Header Server del puerto 80 (lab 05)",
    "B2": "Ruta oculta que lista robots.txt (lab 05)",
    "B3": "Puerto alto 'eleet' del barrido completo (lab 05)",
}

BLOQUE_A = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
BLOQUE_B = ["B1", "B2", "B3"]


def norm(s: str) -> str:
    return s.strip().lower()


def hash_resp(qid: str, resp: str) -> str:
    return hashlib.sha256((qid + "|" + norm(resp)).encode()).hexdigest()


def parsear(path: Path) -> dict:
    respuestas = {}
    for linea in path.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, _, v = linea.partition("=")
        respuestas[k.strip().upper()] = v.strip()
    return respuestas


def evaluar_bloque(ids, respuestas):
    aciertos = 0
    for qid in ids:
        dada = respuestas.get(qid, "")
        bien = bool(dada) and hash_resp(qid, dada) == CLAVE[qid]
        marca = f"{OK}✓{RST}" if bien else (f"{NO}✗{RST}" if dada else f"{DIM}·{RST}")
        extra = "" if dada else f"  {DIM}(sin responder){RST}"
        print(f"  {marca} {qid}  {TITULOS[qid]}{extra}")
        aciertos += bien
    return aciertos


def main() -> int:
    if len(sys.argv) != 2:
        print(f"{AMBER}Uso:{RST} python3 bin/diagnostico.py <tus-respuestas.txt>")
        print(f"{DIM}Plantilla:  cp docs/diagnostico-respuestas.txt mi-diagnostico.txt{RST}")
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"{NO}No encuentro el archivo:{RST} {path}")
        return 2

    respuestas = parsear(path)

    print(f"\n{CY}== Bloque A · Fundamentos (labs 01-04) =={RST}")
    a = evaluar_bloque(BLOQUE_A, respuestas)
    print(f"\n{CY}== Bloque B · ¿Listo para atacar? (operando el lab 05) =={RST}")
    b = evaluar_bloque(BLOQUE_B, respuestas)

    na, nb = len(BLOQUE_A), len(BLOQUE_B)
    pa = round(100 * a / na)
    print(f"\n  Fundamentos: {a}/{na} ({pa}%)   ·   Ofensiva-ready: {b}/{nb}")

    # Veredicto honesto, sin medias tintas.
    if b < nb:
        estado = "ENTORNO"
        msg = (f"{AMBER}Te falta el entorno.{RST} No pudiste contestar el Bloque B: "
               "levantá el lab 05 (./ctf lab 05 · make shell) y operá las tools. "
               "Sin esto no arranca la parte ofensiva.")
    elif a < na * 0.5:
        estado = "REPASAR"
        msg = (f"{NO}Fundamentos flojos.{RST} Repasá los labs 01-04 (RESUMEN-TEORICO.md) "
               "antes de avanzar: sin la base, lo ofensivo se te va a hacer humo.")
    elif a < na:
        estado = "CASI"
        msg = (f"{AMBER}Vas bien, pero hay huecos.{RST} Mirá las que marcaste ✗ y "
               "repasá ESE tema puntual. Después, a romper PhantomCorp.")
    else:
        estado = "LISTO"
        msg = (f"{OK}Listo para ofensiva.{RST} Fundamentos sólidos y entorno operativo. "
               "Dale con recon y enumeración.")

    print(f"\n  {msg}\n")
    print(f"  {DIM}Pegá esta línea en tu entrega:{RST}")
    print(f"  RESULTADO diagnostico-05-06 | fundamentos={a}/{na} | ofensiva={b}/{nb} | estado={estado}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
