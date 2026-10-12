#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
generar_caso.py — construye la evidencia del Lab Extra 4 (cracking).

Genera de forma DETERMINISTA (sobreescribe):
  caso/sombra.txt            el "volcado" de contraseñas (usuario:algo:salt:hash)
  caso/loot/<usuario>.enc    loot cifrado con la contraseña de cada usuario
  caso/diccionario.txt       NO se genera: la escribe la cátedra a mano

Formato de sombra.txt:  usuario:algoritmo:salt_hex:hash_hex
  hash = algoritmo(salt_bytes + password)   para md5/sha256
  pbkdf2 = hashlib.pbkdf2_hmac('sha256', password, salt, iteraciones)

El loot se "cifra" con XOR contra sha256(password) repetido: sin la contraseña
no se lee; con la contraseña crackeada, `cracker.py descifrar` lo abre.
"""
import hashlib
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# (usuario, algoritmo, salt, contraseña, flag-del-loot o None si no cae)
CASOS = [
    ("operador", "md5",    b"s4l7-01", "riverplate",   "FLAG{crack_diccionario_md5}"),
    ("analista", "sha256", b"s4l7-02", "matecocido",   "FLAG{crack_sha256_diccionario}"),
    ("admin",    "sha256", b"s4l7-03", "phantom2026",  "FLAG{crack_reglas_mangling}"),
    ("root",     "pbkdf2", b"s4l7-04", "Tq9#vL2!xZ8-wK7&nB4", None),  # NO cae: esa es la lección
]

ITER_PBKDF2 = 200_000


def hash_de(algo: str, salt: bytes, password: str) -> str:
    if algo == "pbkdf2":
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITER_PBKDF2).hex()
    h = hashlib.new(algo)
    h.update(salt + password.encode())
    return h.hexdigest()


def cifrar(texto: str, password: str) -> str:
    clave = hashlib.sha256(password.encode()).digest()
    datos = texto.encode()
    return bytes(b ^ clave[i % len(clave)] for i, b in enumerate(datos)).hex()


def main():
    lineas = ["# volcado de contraseñas — phantomcorp-web (looteado en la post-explotación)",
              "# formato: usuario:algoritmo:salt_hex:hash_hex"]
    (AQUI / "loot").mkdir(exist_ok=True)
    for usuario, algo, salt, pwd, flag in CASOS:
        h = hash_de(algo, salt, pwd)
        lineas.append(f"{usuario}:{algo}:{salt.hex()}:{h}")
        if flag:
            contenido = (f"Notas de {usuario} — CONFIDENCIAL\n"
                         f"==========================\n"
                         f"Recuperaste esto porque la contraseña era débil.\n"
                         f"Evidencia: {flag}\n")
            (AQUI / "loot" / f"{usuario}.enc").write_text(cifrar(contenido, pwd))
    (AQUI / "sombra.txt").write_text("\n".join(lineas) + "\n")
    print("caso generado: sombra.txt + loot/")


if __name__ == "__main__":
    main()
