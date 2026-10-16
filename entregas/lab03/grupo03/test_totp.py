#!/usr/bin/env python3
"""
test_totp.py - Verificacion de totp() (Parte B.2). Grupo 03, Laboratorio 03.

Correr:  python3 test_totp.py     (sale con 0 si todo pasa)

Se contrasta contra la tabla de vectores publicada en el Apendice B de la
RFC 6238 (SHA-1, secreto ASCII "12345678901234567890", paso de 30 s, 8
digitos), no contra la propia implementacion.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from auth import hotp, totp

SECRETO = b"12345678901234567890"

RFC6238_SHA1 = [
    (59, "94287082"),
    (1111111109, "07081804"),
    (1111111111, "14050471"),
    (1234567890, "89005924"),
    (2000000000, "69279037"),
    (20000000000, "65353130"),
]


def test_vectores_rfc6238_8_digitos():
    for t, esperado in RFC6238_SHA1:
        assert totp(SECRETO, t, digitos=8) == esperado, f"t={t}"


def test_vector_del_enunciado_6_digitos():
    assert totp(SECRETO, 59) == "287082"


def test_el_codigo_tiene_seis_digitos_con_ceros_a_la_izquierda():
    codigo = totp(SECRETO, 1111111109)
    assert codigo == "081804" and len(codigo) == 6


def test_mismo_paso_mismo_codigo():
    assert totp(SECRETO, 30) == totp(SECRETO, 59)
    assert totp(SECRETO, 59) != totp(SECRETO, 60)


def test_t_cero_es_un_instante_valido():
    assert totp(SECRETO, 0) == hotp(SECRETO, 0)


def test_sin_t_usa_el_reloj():
    ahora = int(time.time())
    assert totp(SECRETO) in {totp(SECRETO, ahora), totp(SECRETO, ahora + 1)}


if __name__ == "__main__":
    pruebas = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for nombre, prueba in pruebas:
        prueba()
        print(f"  ok  {nombre}")
    print(f"\n{len(pruebas)} pruebas OK")
