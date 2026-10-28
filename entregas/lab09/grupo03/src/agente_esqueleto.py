#!/usr/bin/env python3
"""Agente de pentest del grupo 03 para el Lab 09."""
import re
import sys
from pathlib import Path

# La entrega conserva solo el archivo solicitado; reutiliza la interfaz dada
# por la catedra desde el repositorio raiz.
RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ / "labs" / "lab09-agentes" / "src"))
from herramientas import TOOLS, ejecutar_tool
from llm import crear_cliente

SYSTEM = """Sos un agente de pentesting autorizado. Objetivo unico: 'phantomcorp'.
Reconoce, enumera, segui las pistas y reporta toda FLAG{...}. Una tool por vez."""
MAX_PASOS = 12


def main() -> int:
    cliente = crear_cliente(SYSTEM, TOOLS)
    flags: set[str] = set()
    resultados = None
    for paso in range(1, MAX_PASOS + 1):
        accion = cliente.paso(resultados)
        if accion["tipo"] == "final":
            print(f"\n[agente] Fin: {accion['texto']}")
            break
        nombre, argumentos = accion["nombre"], accion["argumentos"]
        print(f"\n[paso {paso}] -> {nombre}({argumentos})")
        salida = ejecutar_tool(nombre, argumentos)
        print("\n".join(f"    {linea}" for linea in salida.splitlines()[:12]))
        for flag in re.findall(r"FLAG\{[^}]*\}", salida):
            if flag not in flags:
                print(f"    [+] FLAG NUEVA: {flag}")
                flags.add(flag)
        resultados = [{"id": accion["id"], "output": salida}]
    else:
        print(f"\n[agente] Limite de {MAX_PASOS} pasos alcanzado (guardrail).")
    print(f"\n=== Flags encontradas ({len(flags)}) ===")
    for flag in sorted(flags):
        print(f"  {flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
