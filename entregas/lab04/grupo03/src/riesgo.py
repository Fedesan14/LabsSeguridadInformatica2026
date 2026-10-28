#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
riesgo.py — Laboratorio 04. Riesgo cuantitativo. Solo biblioteca estándar.

La gestión de la seguridad no es opinión: se mide. Este script te da el
vocabulario cuantitativo (ALE, SLE, ARO) para PRIORIZAR con números, no con
corazonadas. Completá los TODO.
"""
import argparse, json, sys

def ale(sle: float, aro: float) -> float:
    """Annualized Loss Expectancy = SLE (pérdida por evento) x ARO (eventos/año).
    Pista: una línea."""
    return sle * aro

def roi_control(ale_antes: float, ale_despues: float, costo_anual: float) -> float:
    """ROI de un control = (pérdida evitada - costo) / costo.
    pérdida evitada = ale_antes - ale_despues. >0 significa que el control se paga."""
    if costo_anual <= 0:
        raise ValueError("el costo anual del control tiene que ser > 0")
    return (ale_antes - ale_despues - costo_anual) / costo_anual

def priorizar(riesgos: list) -> list:
    """Recibe una lista de dicts {nombre, sle, aro}, agrega su 'ale' y los devuelve
    ordenados por ALE descendente (el riesgo más costoso primero).

    Se copia cada dict en vez de mutar la lista que entra: quien llama no
    espera que su JSON aparezca con una clave nueva. sorted() es estable, así
    que dos riesgos con el mismo ALE conservan el orden del archivo."""
    return sorted(({**r, "ale": ale(r["sle"], r["aro"])} for r in riesgos),
                  key=lambda r: r["ale"], reverse=True)

def main() -> int:
    ap = argparse.ArgumentParser(description="Riesgo cuantitativo (Lab 04).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ale"); p.add_argument("--sle", type=float, required=True); p.add_argument("--aro", type=float, required=True)
    p = sub.add_parser("roi"); p.add_argument("--antes", type=float, required=True); p.add_argument("--despues", type=float, required=True); p.add_argument("--costo", type=float, required=True)
    p = sub.add_parser("priorizar"); p.add_argument("--archivo", required=True, help="JSON con lista de {nombre,sle,aro}")
    a = ap.parse_args()
    if a.cmd == "ale": print(f"{ale(a.sle, a.aro):.2f}")
    elif a.cmd == "roi": print(f"{roi_control(a.antes, a.despues, a.costo):.3f}")
    elif a.cmd == "priorizar":
        for r in priorizar(json.load(open(a.archivo))):
            print(f"  {r['ale']:>12.2f}  {r['nombre']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
