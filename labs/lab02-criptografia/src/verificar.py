#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
verificar.py — autoevaluación del Lab 02. Corré:  python3 verificar.py

Chequea tu implementación y te dice qué anda y qué falta. NO es la nota: es
feedback para que iteres solo, sin esperar la corrección. Verde = va; rojo =
revisá; gris = todavía no lo implementaste.
"""
import os, sys, hashlib, hmac
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OK, NO, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
P = {"ok": 0, "no": 0, "todo": 0}

def check(nombre, fn):
    try:
        fn(); print(f"  {OK}✓{RST} {nombre}"); P["ok"] += 1
    except NotImplementedError:
        print(f"  {DIM}·  {nombre}  (todavía sin implementar){RST}"); P["todo"] += 1
    except AssertionError as e:
        print(f"  {NO}✗{RST} {nombre}  → {e}"); P["no"] += 1
    except Exception as e:
        print(f"  {NO}✗{RST} {nombre}  → {type(e).__name__}: {e}"); P["no"] += 1

try:
    import cripto
except Exception as e:
    print(f"{NO}No pude importar cripto.py: {e}{RST}"); sys.exit(1)

def t_romper():
    claro = b"El mensaje secreto de PhantomCorp para todos y todas."
    cif = cripto.xor_cifrar(claro, bytes([0x5A]))
    k, out = cripto.romper_xor_1byte(cif)
    assert k == 0x5A, f"clave hallada 0x{k:02x}, esperaba 0x5a"
    assert out == claro, "recuperaste la clave pero el texto no coincide"

def t_mac_ingenuo():
    assert cripto.mac_ingenuo(b"k", b"m") == hashlib.sha256(b"km").hexdigest(), \
        "mac_ingenuo debe ser sha256(clave || msg) en hex"

def t_mac_hmac():
    assert cripto.mac_hmac(b"k", b"m") == hmac.new(b"k", b"m", hashlib.sha256).hexdigest(), \
        "mac_hmac debe ser HMAC-SHA256 en hex"

def t_verificar():
    a = cripto.mac_hmac(b"clave", b"pago 100")
    assert cripto.verificar_mac(a, a) is True, "dos MAC iguales deben dar True"
    assert cripto.verificar_mac(a, "0"*len(a)) is False, "dos MAC distintos deben dar False"

print("\n== Lab 02 · Criptografía ==")
check("romper_xor_1byte recupera clave y texto", t_romper)
check("mac_ingenuo = sha256(clave||msg)", t_mac_ingenuo)
check("mac_hmac = HMAC-SHA256", t_mac_hmac)
check("verificar_mac compara bien", t_verificar)
print(f"\n{OK}{P['ok']} OK{RST} · {NO}{P['no']} a revisar{RST} · {DIM}{P['todo']} sin implementar{RST}\n")
sys.exit(1 if P["no"] else 0)
