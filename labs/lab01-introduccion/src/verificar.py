#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""verificar.py — autoevaluación del Lab 01.  python3 verificar.py"""
import os, sys, hashlib, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OK, NO, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
P = {"ok":0,"no":0,"todo":0}
def check(n, fn):
    try: fn(); print(f"  {OK}✓{RST} {n}"); P["ok"]+=1
    except NotImplementedError: print(f"  {DIM}·  {n}  (todavía sin implementar){RST}"); P["todo"]+=1
    except AssertionError as e: print(f"  {NO}✗{RST} {n}  → {e}"); P["no"]+=1
    except Exception as e: print(f"  {NO}✗{RST} {n}  → {type(e).__name__}: {e}"); P["no"]+=1
try: import integridad as I
except Exception as e: print(f"{NO}No pude importar integridad.py: {e}{RST}"); sys.exit(1)
MOD = getattr(I, "ESTADO_MODIFICADO", "MODIFICADO")

def t_sha():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d)/"x.bin"; f.write_bytes(b"hola phantom")
        assert I.sha256_archivo(f) == hashlib.sha256(b"hola phantom").hexdigest(), "el hash no coincide con hashlib"
def t_hamming():
    assert I.distancia_hamming_bits(b"\x00", b"\xff") == 8, "0x00 vs 0xff difieren en 8 bits"
    assert I.distancia_hamming_bits(b"\xab", b"\xab") == 0, "iguales -> 0 bits (¿estás contando hex en vez de bits?)"
def t_mac():
    import hmac
    tag,_ = I.calcular_mac(b"clave", b"msg")
    assert tag == hmac.new(b"clave", b"msg", hashlib.sha256).hexdigest(), "calcular_mac debe ser HMAC-SHA256"
def t_manifiesto():
    with tempfile.TemporaryDirectory() as d:
        base=Path(d); (base/"a.txt").write_text("uno"); (base/"b.txt").write_text("dos")
        man_path=base/"m.sha256"
        man=I.generar_manifiesto(base, man_path)
        assert isinstance(man, dict) and len(man)>=2, "generar_manifiesto debe devolver el dict de hashes"
        (base/"a.txt").write_text("uno modificado")   # cambio de bytes
        res=I.verificar_manifiesto(base, man, man_path)
        assert any("a.txt" in x for x in res.get(MOD, [])), "debe detectar a.txt como MODIFICADO"
print("\n== Lab 01 · Integridad ==")
check("sha256_archivo", t_sha)
check("distancia_hamming_bits (en BITS, no en hex)", t_hamming)
check("calcular_mac = HMAC-SHA256", t_mac)
check("manifiesto detecta un archivo modificado", t_manifiesto)
print(f"\n{OK}{P['ok']} OK{RST} · {NO}{P['no']} a revisar{RST} · {DIM}{P['todo']} sin implementar{RST}\n")
sys.exit(1 if P["no"] else 0)
