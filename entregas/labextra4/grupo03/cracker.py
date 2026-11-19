#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# Implementación de los ejercicios: Grupo 03, con asistencia de Codex.
"""Lab Extra 4: diccionario, reglas y apertura del loot del caso local.

Conserva las firmas y los subcomandos del esqueleto de la cátedra.
Solo usa la biblioteca estándar de Python.
"""
import argparse
import hashlib
import hmac
import string
import sys
from time import perf_counter

ITER_PBKDF2 = 200_000
LONGITUD_HASH = {"md5": 32, "sha256": 64, "pbkdf2": 64}


def descifrar_loot(hex_cifrado: str, password: str) -> str:
    """Referencia provista: XOR contra sha256(password) repetido.

    Es una construcción didáctica sin autenticación: una contraseña errónea
    puede producir basura y no necesariamente un error.
    """
    clave = hashlib.sha256(password.encode()).digest()
    datos = bytes.fromhex(hex_cifrado.strip())
    return bytes(b ^ clave[i % len(clave)] for i, b in enumerate(datos)).decode("utf-8", "ignore")


def hash_de(algo: str, salt_hex: str, password: str) -> str:
    """Reproduce la receta del servidor; el salt se decodifica desde hex."""
    if algo not in LONGITUD_HASH:
        raise ValueError(f"algoritmo no soportado: {algo}")
    salt = bytes.fromhex(salt_hex)
    password_bytes = password.encode("utf-8")
    if algo == "pbkdf2":
        return hashlib.pbkdf2_hmac("sha256", password_bytes, salt, ITER_PBKDF2).hex()
    return hashlib.new(algo, salt + password_bytes).hexdigest()


def cargar_sombra(ruta: str) -> list:
    """Lee usuario:algoritmo:salt_hex:hash_hex; valida sin omitir errores."""
    sombra = []
    usuarios = set()
    with open(ruta, encoding="utf-8-sig") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            campos = [campo.strip() for campo in linea.split(":")]
            error = f"{ruta}:{numero}"
            if len(campos) != 4 or not all(campos):
                raise ValueError(f"{error}: se esperan cuatro campos no vacíos")
            usuario, algo, salt_hex, hash_hex = campos
            if usuario in usuarios:
                raise ValueError(f"{error}: usuario duplicado: {usuario}")
            if algo not in LONGITUD_HASH:
                raise ValueError(f"{error}: algoritmo no soportado: {algo}")
            if len(salt_hex) % 2 or any(c not in string.hexdigits for c in salt_hex):
                raise ValueError(f"{error}: salt hexadecimal inválido")
            if len(hash_hex) != LONGITUD_HASH[algo] or any(c not in string.hexdigits for c in hash_hex):
                raise ValueError(f"{error}: hash hexadecimal inválido para {algo}")
            usuarios.add(usuario)
            sombra.append((usuario, algo, salt_hex.lower(), hash_hex.lower()))
    return sombra


def aplicar_reglas(palabra: str) -> list:
    """Original e inicial mayúscula, con sufijos probables; sin duplicados.

    Años: 2024, 2025 y 2026. Números comunes: 1, 12 y 123.
    El orden es estable para que los intentos sean reproducibles.
    """
    sufijos = ("", "2024", "2025", "2026", "1", "12", "123")
    bases = (palabra, palabra[:1].upper() + palabra[1:])
    return list(dict.fromkeys(base + sufijo for base in bases for sufijo in sufijos))


def cargar_candidatos(diccionario: str, con_reglas: bool = False) -> list:
    """Genera una lista común a las cuentas, deduplicada y en orden."""
    candidatos = {}
    with open(diccionario, encoding="utf-8-sig") as archivo:
        for linea in archivo:
            palabra = linea.rstrip("\r\n")
            if not palabra:
                continue
            variantes = aplicar_reglas(palabra) if con_reglas else [palabra]
            for candidato in variantes:
                candidatos.setdefault(candidato, None)
    return list(candidatos)


def crackear(sombra: list, diccionario: str, con_reglas: bool = False) -> dict:
    """Prueba todos los candidatos de cada cuenta hasta hallar coincidencia.

    Incluye PBKDF2: no se lo saltea ni se lo declara invulnerable.
    Cada cuenta requiere sus propios hashes debido al salt diferente.
    """
    candidatos = cargar_candidatos(diccionario, con_reglas)
    tecnica = "diccionario + reglas" if con_reglas else "diccionario"
    print(f"Técnica: {tecnica}; candidatos únicos por cuenta: {len(candidatos)}", flush=True)
    halladas = {}
    for usuario, algo, salt_hex, esperado in sombra:
        print(f"Atacando {usuario} ({algo})...", flush=True)
        intentos = 0
        inicio = perf_counter()
        for password in candidatos:
            intentos += 1
            if hmac.compare_digest(hash_de(algo, salt_hex, password), esperado):
                halladas[usuario] = password
                break
        segundos = perf_counter() - inicio
        velocidad = intentos / segundos if segundos else 0.0
        resultado = "hallada" if usuario in halladas else "sin coincidencia en los candidatos probados"
        print(f"{usuario}: {resultado} | intentos={intentos} | tiempo={segundos:.6f}s | {velocidad:.2f} intentos/s", flush=True)
    return halladas


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
    try:
        if args.cmd == "crackear":
            sombra = cargar_sombra(args.sombra)
            halladas = crackear(sombra, args.diccionario, args.reglas)
            for usuario, _algo, _salt, _h in sombra:
                if usuario in halladas:
                    print(f"  ✓ {usuario}: {halladas[usuario]}")
                else:
                    print(f"  ✗ {usuario}: sin coincidencia en los candidatos probados")
            print(f"\n{len(halladas)}/{len(sombra)} contraseñas recuperadas")
        else:
            with open(args.loot, encoding="utf-8") as archivo:
                print(descifrar_loot(archivo.read(), args.password))
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
