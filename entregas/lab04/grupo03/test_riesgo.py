#!/usr/bin/env python3
"""
test_riesgo.py - Verificacion de src/riesgo.py. Grupo 03, Laboratorio 04.

Correr:  python3 test_riesgo.py     (sale con 0 si todo pasa)

Los valores esperados no salen del propio codigo: son los ejemplos que publica
el enunciado (README del lab: 20000.00 y 0.875) y cuentas hechas a mano con
las cifras de riesgos.json. La CLI se corre como proceso aparte para comprobar
la salida exacta que pide el enunciado, no solo las funciones.
"""
import json
import os
import subprocess
import sys

_RAIZ = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(_RAIZ, "src", "riesgo.py")
sys.path.insert(0, os.path.join(_RAIZ, "src"))

from riesgo import ale, priorizar, roi_control


def cli(*args):
    return subprocess.run([sys.executable, _SCRIPT, *args], capture_output=True,
                          text=True, check=True).stdout

assert ale(50000, 0.4) == 20000
assert ale(0, 3) == 0
assert cli("ale", "--sle", "50000", "--aro", "0.4").strip() == "20000.00"

assert abs(roi_control(20000, 5000, 8000) - 0.875) < 1e-9
assert roi_control(1250, 250, 4800) < 0, "un control que cuesta mas de lo que evita da ROI negativo"
assert roi_control(10000, 0, 10000) == 0, "evitar exactamente lo que cuesta es ROI 0"
assert cli("roi", "--antes", "20000", "--despues", "5000", "--costo", "8000").strip() == "0.875"
try:
    roi_control(20000, 5000, 0)
    raise AssertionError("costo 0 tiene que rechazarse, no dividir por cero")
except ValueError:
    pass

entrada = [{"nombre": "a", "sle": 10000, "aro": 2},
           {"nombre": "b", "sle": 50000, "aro": 0.4},
           {"nombre": "c", "sle": 1000, "aro": 30}]
salida = priorizar(entrada)
assert [r["nombre"] for r in salida] == ["c", "a", "b"]
assert [r["ale"] for r in salida] == [30000, 20000, 20000]
assert all("ale" not in r for r in entrada), "priorizar no debe mutar la lista que recibe"
assert priorizar([]) == []

with open(os.path.join(_RAIZ, "riesgos.json"), encoding="utf-8") as f:
    riesgos = json.load(f)
assert len(riesgos) >= 4, "el enunciado pide al menos cuatro riesgos"
assert all({"nombre", "sle", "aro"} <= r.keys() for r in riesgos)
esperado_a_mano = [36000, 30000, 20000, 1500, 1250]
assert [r["ale"] for r in priorizar(riesgos)] == esperado_a_mano
assert cli("priorizar", "--archivo", os.path.join(_RAIZ, "riesgos.json")).count("\n") == len(riesgos)

print("OK: ale, roi_control, priorizar y riesgos.json verificados")
