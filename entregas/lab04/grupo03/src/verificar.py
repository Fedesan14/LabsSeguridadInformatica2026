#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""verificar.py — autoevaluación del Lab 04.  python3 verificar.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OK, NO, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
P = {"ok":0,"no":0,"todo":0}
def check(n, fn):
    try: fn(); print(f"  {OK}✓{RST} {n}"); P["ok"]+=1
    except NotImplementedError: print(f"  {DIM}·  {n}  (todavía sin implementar){RST}"); P["todo"]+=1
    except AssertionError as e: print(f"  {NO}✗{RST} {n}  → {e}"); P["no"]+=1
    except Exception as e: print(f"  {NO}✗{RST} {n}  → {type(e).__name__}: {e}"); P["no"]+=1
try: import riesgo
except Exception as e: print(f"{NO}No pude importar riesgo.py: {e}{RST}"); sys.exit(1)
def t_ale(): assert riesgo.ale(50000, 0.4) == 20000, "ALE = SLE x ARO = 50000 x 0.4 = 20000"
def t_roi():
    r = riesgo.roi_control(20000, 5000, 8000)
    assert abs(r - 0.875) < 1e-6, f"ROI (20000->5000, costo 8000) = (15000-8000)/8000 = 0.875, diste {r}"
def t_prior():
    rs = [{"nombre":"a","sle":10000,"aro":2}, {"nombre":"b","sle":50000,"aro":0.4}]
    out = riesgo.priorizar(rs)
    assert all("ale" in x for x in out), "cada riesgo debe tener su 'ale' calculado"
    assert out[0]["ale"] >= out[-1]["ale"], "deben quedar ordenados por ALE descendente"
print("\n== Lab 04 · Riesgo cuantitativo ==")
check("ale()", t_ale); check("roi_control()", t_roi); check("priorizar() ordena por ALE", t_prior)
print(f"\n{OK}{P['ok']} OK{RST} · {NO}{P['no']} a revisar{RST} · {DIM}{P['todo']} sin implementar{RST}\n")
sys.exit(1 if P["no"] else 0)
