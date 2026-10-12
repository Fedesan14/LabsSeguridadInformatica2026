#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
cracker.py — Lab Extra 4. Tu cracker de contraseñas. Solo biblioteca estándar.

Looteaste `caso/sombra.txt` de phantomcorp-web: un volcado de hashes con sus
algoritmos y salts. Tu trabajo: recuperar las contraseñas y con ellas abrir el
loot cifrado de cada usuario (`caso/loot/<usuario>.enc`).

Completá los TODO. NO cambies las firmas ni la CLI.
`descifrar_loot()` ya viene implementada como referencia: leela.

Uso:
  python3 cracker.py crackear caso/sombra.txt caso/diccionario.txt
  python3 cracker.py descifrar caso/loot/operador.enc --password riverplate

Extra (R3): la contraseña del admin NO está literal en el diccionario.
Implementá reglas de "mangling" en `aplicar_reglas()`: sufijos de año, de
números, mayúscula inicial, etc.
"""
import argparse
import hashlib
import sys

ITER_PBKDF2 = 200_000   # tiene que coincidir con sombra.txt


# ---------------------------------------------------------------------------
# REFERENCIA (ya implementada). Leela: es la mitad del lab.
# ---------------------------------------------------------------------------
def descifrar_loot(hex_cifrado: str, password: str) -> str:
    """El loot se cifró con XOR contra sha256(password) repetido.
    XOR es involutivo: con la contraseña correcta, esto devuelve el texto."""
    clave = hashlib.sha256(password.encode()).digest()
    datos = bytes.fromhex(hex_cifrado.strip())
    return bytes(b ^ clave[i % len(clave)] for i, b in enumerate(datos)).decode("utf-8", "ignore")


def hash_de(algo: str, salt_hex: str, password: str) -> str:
    """Calcula el hash de un candidato EXACTAMENTE como lo hizo el servidor.
    Pista: md5/sha256 son hash(salt_bytes + password); pbkdf2 usa
    hashlib.pbkdf2_hmac('sha256', password, salt, ITER_PBKDF2)."""
    # TODO
    raise NotImplementedError("Completá hash_de()")


def cargar_sombra(ruta: str) -> list:
    """Devuelve una lista de tuplas (usuario, algo, salt_hex, hash_hex)
    parseando sombra.txt (ignorá líneas de comentario que empiezan con #)."""
    # TODO
    raise NotImplementedError("Completá cargar_sombra()")


def aplicar_reglas(palabra: str) -> list:
    """Dado un lemma del diccionario, devolvé variantes probables:
    la palabra sola, palabra+año (2024..2026), palabra+números comunes
    (1, 12, 123), palabra con mayúscula inicial... Agregá las que se te ocurran.
    Esto es lo que john hace con --rules y hashcat con -r."""
    # TODO
    raise NotImplementedError("Completá aplicar_reglas()")


def crackear(sombra: list, diccionario: str, con_reglas: bool = False) -> dict:
    """Para cada usuario, probá cada candidato del diccionario (y sus variantes
    si con_reglas=True) hasta que hash_de() coincida con el hash looteado.
    Devolvé {usuario: password} de los que cayeron. Imprimí el progreso.

    OJO con pbkdf2: 200.000 iteraciones por intento. ¿Conviene probarlo con el
    diccionario entero? ¿Qué te dice eso del algoritmo? (Pista: es la P4.)"""
    # TODO
    raise NotImplementedError("Completá crackear()")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cracker de contraseñas (Lab Extra 4)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crackear", help="atacar un volcado de hashes")
    c.add_argument("sombra")
    c.add_argument("diccionario")
    c.add_argument("--reglas", action="store_true", help="aplicar reglas de mangling")
    d = sub.add_parser("descifrar", help="abrir un loot con la contraseña crackeada")
    d.add_argument("loot")
    d.add_argument("--password", required=True)
    args = ap.parse_args()

    if args.cmd == "crackear":
        sombra = cargar_sombra(args.sombra)
        halladas = crackear(sombra, args.diccionario, args.reglas)
        for usuario, _algo, _salt, _h in sombra:
            if usuario in halladas:
                print(f"  ✓ {usuario}: {halladas[usuario]}")
            else:
                print(f"  ✗ {usuario}: no cayó (¿falta una regla? ¿es pbkdf2?)")
        print(f"\n{len(halladas)}/{len(sombra)} contraseñas recuperadas")
    else:
        with open(args.loot) as fh:
            print(descifrar_loot(fh.read(), args.password))
    return 0


if __name__ == "__main__":
    sys.exit(main())
