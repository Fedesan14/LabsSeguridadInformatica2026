#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
auth.py — Laboratorio 03. Autenticación hecha bien. Solo biblioteca estándar.

Completá los TODO. NO cambies las firmas ni la CLI. `hotp()` viene implementada
como referencia (es la base del TOTP): leela.
"""
import argparse, hashlib, hmac, secrets, struct, sys, time

# --- B.1: almacenamiento de contraseñas ---
def hash_password(password: str, salt: bytes = None, iters: int = 200_000) -> str:
    """Devuelve una cadena 'pbkdf2_sha256$iters$salt_hex$dk_hex'.
    Pista: secrets.token_bytes para el salt; hashlib.pbkdf2_hmac('sha256', ...).
    ¿Por qué salt por usuario? ¿Por qué 200.000 iteraciones y no una?"""

    #Si no se proporciona un salt, generamos uno nuevo de 16 bytes aleatorios.
    if salt is None:
        salt = secrets.token_bytes(16)

    if iters <= 0:
        raise ValueError("El número de iteraciones debe ser mayor que cero.")

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iters
    )

    return f"pbkdf2_sha256${iters}${salt.hex()}${dk.hex()}"

def verify_password(password: str, almacenado: str) -> bool:
    """Verifica una contraseña contra el registro de hash_password().
    DEBE comparar en tiempo constante (hmac.compare_digest)."""

    try:
        #Separar los cuatro componentes del registro.
        algoritmo, iters_texto, salt_hex, dk_hex = almacenado.split("$")

        # Comprobar que el algoritmo sea el esperado.
        if algoritmo != "pbkdf2_sha256":
            return False

        # Recuperar las iteraciones y el salt.
        iters = int(iters_texto)
        if iters <= 0:
            return False

        salt = bytes.fromhex(salt_hex)
        hash_esperado = bytes.fromhex(dk_hex)

        # Calcular nuevamente el hash con los mismos parámetros.
        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iters,
            dklen=len(hash_esperado)
        )

        # Comparar en tiempo constante.
        return hmac.compare_digest(hash_calculado, hash_esperado)

    except (ValueError, TypeError):
        # Un registro mal formado no debe validar la contraseña.
        return False

# --- B.2: segundo factor (TOTP / RFC 6238) ---
def hotp(secret: bytes, contador: int, digitos: int = 6, algo: str = "sha1") -> str:
    """HOTP (RFC 4226): HMAC del contador + truncamiento dinámico. YA IMPLEMENTADA."""
    h = hmac.new(secret, struct.pack(">Q", contador), algo).digest()
    off = h[-1] & 0x0F
    code = (struct.unpack(">I", h[off:off + 4])[0] & 0x7FFFFFFF) % (10 ** digitos)
    return str(code).zfill(digitos)

def totp(secret: bytes, t: int = None, paso: int = 30, digitos: int = 6) -> str:
    """TOTP (RFC 6238): HOTP usando como contador el tiempo dividido en pasos.
    Pista: contador = t // paso. Si t es None, usá time.time()."""
    # TODO
    raise NotImplementedError("Completá totp()")

def main() -> int:
    ap = argparse.ArgumentParser(description="Autenticación (Lab 03).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("hash"); p.add_argument("--password", required=True)
    p = sub.add_parser("verify"); p.add_argument("--password", required=True); p.add_argument("--registro", required=True)
    p = sub.add_parser("totp"); p.add_argument("--secret", required=True, help="secreto ASCII"); p.add_argument("--t", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "hash": print(hash_password(a.password))
    elif a.cmd == "verify": print("OK" if verify_password(a.password, a.registro) else "FALLO"); return 0 if verify_password(a.password, a.registro) else 1
    elif a.cmd == "totp": print(totp(a.secret.encode(), a.t))
    return 0

if __name__ == "__main__":
    sys.exit(main())
