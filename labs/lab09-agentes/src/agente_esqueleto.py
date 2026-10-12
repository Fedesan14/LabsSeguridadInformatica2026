#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
agente_esqueleto.py — TU agente (a completar). Entregable del Lab 09.

El agente de referencia (agente_pentest.py) ya funciona. Este es el TUYO: tiene
el andamiaje, pero el LOOP de tool-use está a medio hacer. Completá los TODO para
entender el mecanismo desde adentro. Un agente no es magia: es este loop.

Cuando funcione, corré:
    LLM_PROVIDER=mock python3 agente_esqueleto.py
y tiene que llegar a encadenar /api/token -> POST /api/vault y traer el flag
capstone que devuelve el vault.
"""
import re
import sys
from herramientas import TOOLS, ejecutar_tool
from llm import crear_cliente

SYSTEM = """Sos un agente de pentesting autorizado. Objetivo único: 'phantomcorp'.
Reconocé, enumerá, seguí las pistas y reportá toda FLAG{...}. Una tool por vez."""

MAX_PASOS = 12

def main() -> int:
    cliente = crear_cliente(SYSTEM, TOOLS)
    flags = set()
    resultados = None

    for n in range(1, MAX_PASOS + 1):
        accion = cliente.paso(resultados)

        # TODO 1: si la acción es de tipo "final", imprimí el texto y salí del loop.
        # ...

        # TODO 2: si es una tool, ejecutala con ejecutar_tool(nombre, argumentos)
        #         y guardá la salida. Pista: accion["nombre"], accion["argumentos"].
        salida = ""  # <-- reemplazá esto

        # (esto ya está: detectar flags en la salida)
        for f in re.findall(r"FLAG\{[^}]*\}", salida):
            flags.add(f)

        # TODO 3: devolvele el resultado al LLM para el próximo paso. El formato es
        #         una lista con un dict {"id": accion["id"], "output": salida}.
        resultados = None  # <-- reemplazá esto

    print(f"\n=== Flags encontradas ({len(flags)}) ===")
    for f in sorted(flags):
        print(f"  {f}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
