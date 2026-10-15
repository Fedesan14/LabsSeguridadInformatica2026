#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""verificar.py — autoevaluación del Lab 03.  python3 verificar.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OK, NO, DIM, RST = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
P = {"ok":0,"no":0,"todo":0}
def check(n, fn):
    try: fn(); print(f"  {OK}✓{RST} {n}"); P["ok"]+=1
    except NotImplementedError: print(f"  {DIM}·  {n}  (todavía sin implementar){RST}"); P["todo"]+=1
    except AssertionError as e: print(f"  {NO}✗{RST} {n}  → {e}"); P["no"]+=1
    except Exception as e: print(f"  {NO}✗{RST} {n}  → {type(e).__name__}: {e}"); P["no"]+=1
try: import auth
except Exception as e: print(f"{NO}No pude importar auth.py: {e}{RST}"); sys.exit(1)
def t_pwd():
    reg = auth.hash_password("Phantom-2026!")
    assert auth.verify_password("Phantom-2026!", reg) is True, "debe verificar la contraseña correcta"
    assert auth.verify_password("otra", reg) is False, "debe rechazar la contraseña incorrecta"
def t_pwd_salt():
    a = auth.hash_password("misma"); b = auth.hash_password("misma")
    assert a != b, "dos hashes de la MISMA contraseña deben diferir (salt aleatorio por usuario)"
def t_totp():
    # RFC 6238: secret ASCII '12345678901234567890', t=59, 6 dígitos -> 287082
    got = auth.totp(b"12345678901234567890", 59)
    assert got == "287082", f"vector RFC 6238 (t=59) esperaba 287082, diste {got}"
print("\n== Lab 03 · Autenticación ==")
check("hash_password / verify_password", t_pwd)
check("salt por usuario (hashes distintos)", t_pwd_salt)
check("totp coincide con el vector del RFC 6238", t_totp)
print(f"\n{OK}{P['ok']} OK{RST} · {NO}{P['no']} a revisar{RST} · {DIM}{P['todo']} sin implementar{RST}\n")
sys.exit(1 if P["no"] else 0)
