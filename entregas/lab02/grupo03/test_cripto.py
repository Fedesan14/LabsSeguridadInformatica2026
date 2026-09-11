#!/usr/bin/env python3
"""
test_cripto.py - Verificacion de src/cripto.py. Grupo 03, Laboratorio 02.

Correr:  python3 test_cripto.py     (sale con 0 si todo pasa)

Los MAC no se comparan contra la propia stdlib -- eso solo probaria que el
codigo es igual a si mismo. Se usan vectores de prueba publicados: RFC 4231
para HMAC-SHA-256 y FIPS 180-4 para SHA-256.
"""
import os
import sys

_AQUI = os.path.dirname(__file__)
sys.path[:0] = [os.path.join(_AQUI, "src"), os.path.join(_AQUI, "data")]

from cripto import mac_hmac, mac_ingenuo, romper_xor_1byte, verificar_mac, xor_cifrar
from generar_datos import CLAVE, MENSAJE


def test_romper_recupera_clave_y_mensaje():
    # El mismo reto que genera data/generar_datos.py, armado en memoria.
    cifrado = xor_cifrar(MENSAJE.encode(), bytes([CLAVE]))
    clave, claro = romper_xor_1byte(cifrado)
    assert clave == CLAVE, f"clave hallada 0x{clave:02x}, esperada 0x{CLAVE:02x}"
    assert claro.decode() == MENSAJE


def test_romper_no_explota_con_entrada_vacia():
    assert romper_xor_1byte(b"") == (0, b"")


def test_mac_ingenuo_es_sha256_de_la_concatenacion():
    # FIPS 180-4: SHA-256("abc"). mac_ingenuo(b"a", b"bc") hashea "a" || "bc".
    esperado = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert mac_ingenuo(b"a", b"bc") == esperado


def test_mac_hmac_contra_vector_rfc4231():
    # RFC 4231, Test Case 1.
    esperado = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
    assert mac_hmac(b"\x0b" * 20, b"Hi There") == esperado


def test_ingenuo_y_hmac_no_son_lo_mismo():
    clave, msg = b"secreta", b"pago 100"
    assert mac_ingenuo(clave, msg) != mac_hmac(clave, msg)


def test_verificar_mac():
    tag = mac_hmac(b"secreta", b"pago 100")
    assert verificar_mac(tag, tag) is True
    # Un solo nibble cambiado tiene que rechazar.
    alterado = ("f" if tag[0] != "f" else "0") + tag[1:]
    assert verificar_mac(tag, alterado) is False
    # Largos distintos y no-ASCII no deben lanzar excepcion: es dato de afuera.
    assert verificar_mac(tag, "") is False
    assert verificar_mac(tag, "ñ" * len(tag)) is False


if __name__ == "__main__":
    pruebas = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for nombre, prueba in pruebas:
        prueba()
        print(f"  ok  {nombre}")
    print(f"\n{len(pruebas)} pruebas OK")
