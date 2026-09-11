#!/usr/bin/env python3
"""
cripto.py - Laboratorio 02 (Criptografia). Grupo 03. Solo biblioteca estandar.

Cuatro herramientas sobre una misma idea: que primitiva aporta que propiedad.

  xor_cifrar        -> confidencialidad (mala): cifrado clasico de clave repetida
  romper_xor_1byte  -> el ataque que demuestra por que es mala
  mac_ingenuo       -> autenticidad (mal hecha): sha256(clave || msg)
  mac_hmac          -> autenticidad (bien hecha): HMAC-SHA256
  verificar_mac     -> comparacion en tiempo constante
"""
import argparse
import hashlib
import hmac
import sys

# ---------------------------------------------------------------------------
# REFERENCIA (venia implementada en el enunciado).
# ---------------------------------------------------------------------------
def xor_cifrar(datos: bytes, clave: bytes) -> bytes:
    """Cifra (y descifra) por XOR de clave repetida. XOR es involutivo:
    aplicar la misma clave dos veces devuelve el original."""
    return bytes(b ^ clave[i % len(clave)] for i, b in enumerate(datos))


# ---------------------------------------------------------------------------
# B.1 - romper XOR de clave de 1 byte por analisis de frecuencia
# ---------------------------------------------------------------------------
# Espacio + las 14 letras mas frecuentes del espanol, ambas cajas: ~85% del texto.
_FRECUENTES = frozenset(b" eaosrnidlctumpEAOSRNIDLCTUMP")


def romper_xor_1byte(cifrado: bytes) -> tuple[int, bytes]:
    """Prueba las 256 claves posibles de 1 byte y devuelve (clave, texto_claro)
    de la mas probable de ser lenguaje natural.

    El XOR preserva la estadistica del texto plano bajo una permutacion fija de
    bytes: por eso alcanza con contar cuantos bytes de cada candidato caen en el
    conjunto de caracteres frecuentes y quedarse con el mejor. Un espacio de
    claves de 8 bits no protege nada.
    """
    clave = max(range(256), key=lambda k: sum((b ^ k) in _FRECUENTES for b in cifrado))
    return clave, xor_cifrar(cifrado, bytes([clave]))


# ---------------------------------------------------------------------------
# B.2 - MAC ingenuo vs HMAC
# ---------------------------------------------------------------------------
def mac_ingenuo(clave: bytes, msg: bytes) -> str:
    """Devuelve sha256(clave || msg) en hex. Es lo que MUCHA gente hace...
    y es vulnerable a length-extension: en una construccion Merkle-Damgard la
    salida ES el estado interno, asi que quien conoce el tag y la longitud de
    (clave || msg) puede seguir hasheando sin conocer la clave."""
    return hashlib.sha256(clave + msg).hexdigest()


def mac_hmac(clave: bytes, msg: bytes) -> str:
    """Devuelve el HMAC-SHA256 en hex. Esta es la forma CORRECTA: el hash
    externo H((K^opad) || H((K^ipad) || msg)) tapa el estado interno del hash
    interno, con lo cual no queda nada extensible por el atacante."""
    return hmac.new(clave, msg, hashlib.sha256).hexdigest()


def verificar_mac(esperado: str, recibido: str) -> bool:
    """Compara dos MAC en hex en tiempo constante.

    Con `==` la comparacion corta en el primer byte distinto, y ese tiempo de
    respuesta le dice al atacante cuantos caracteres iniciales acerto: puede
    reconstruir el tag caracter por caracter en vez de probar el espacio
    completo. compare_digest recorre siempre el largo entero.

    Se codifica a bytes porque compare_digest rechaza str no-ASCII, y `recibido`
    es un dato que viene de afuera.
    """
    return hmac.compare_digest(esperado.encode(), recibido.encode())


def main() -> int:
    ap = argparse.ArgumentParser(description="Herramientas de cripto (Lab 02).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("xor", help="cifrar/descifrar por XOR (hex de salida)")
    p.add_argument("--texto", required=True)
    p.add_argument("--clave", required=True)

    p = sub.add_parser("romper", help="romper un cifrado XOR de 1 byte (hex de entrada)")
    p.add_argument("--hex", required=True, help="cifrado en hexadecimal")

    p = sub.add_parser("mac", help="calcular MAC de un mensaje")
    p.add_argument("--clave", required=True)
    p.add_argument("--msg", required=True)
    p.add_argument("--modo", choices=["ingenuo", "hmac"], default="hmac")

    a = ap.parse_args()
    if a.cmd == "xor":
        print(xor_cifrar(a.texto.encode(), a.clave.encode()).hex())
    elif a.cmd == "romper":
        k, claro = romper_xor_1byte(bytes.fromhex(a.hex))
        print(f"clave=0x{k:02x}")
        print(claro.decode(errors="replace"))
    elif a.cmd == "mac":
        fn = mac_ingenuo if a.modo == "ingenuo" else mac_hmac
        print(fn(a.clave.encode(), a.msg.encode()))
    return 0

if __name__ == "__main__":
    sys.exit(main())
