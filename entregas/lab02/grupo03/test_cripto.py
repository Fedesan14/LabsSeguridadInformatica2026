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
import unittest

_RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_RAIZ, "src"), os.path.join(_RAIZ, "data")]

from cripto import mac_hmac, mac_ingenuo, romper_xor_1byte, verificar_mac, xor_cifrar
from generar_datos import CLAVE, MENSAJE

class RomperXOR(unittest.TestCase):
    def test_recupera_la_clave_y_el_mensaje_del_reto(self):
        cifrado = xor_cifrar(MENSAJE.encode(), bytes([CLAVE]))
        clave, claro = romper_xor_1byte(cifrado)
        self.assertEqual(clave, CLAVE)
        self.assertEqual(claro.decode(), MENSAJE)

    def test_no_rompe_con_una_entrada_vacia(self):
        self.assertEqual(romper_xor_1byte(b""), (0, b""))

class MacIngenuo(unittest.TestCase):
    def test_vector_cadena_vacia_flips_180_4(self):
        # SHA-256("") -- clave y mensaje vacios, asi mac_ingenuo hashea "".
        esperado = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(mac_ingenuo(b"", b""), esperado)

    def test_vector_abc_flips_180_4(self):
        # SHA-256("abc"), armado como clave="a" + mensaje="bc".
        esperado = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        self.assertEqual(mac_ingenuo(b"a", b"bc"), esperado)

class MacHmac(unittest.TestCase):
    def test_vector_rfc423_caso_1(self):
        clave = b"\x0b" * 20
        esperado = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
        self.assertEqual(mac_hmac(clave, "Hi There"), esperado)

    def test_vector_rfc423_caso_2(self):
        esperado = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        self.assertEqual(mac_hmac(b"Jefe", "what do ya want for nothing?"), esperado)

    def test_no_coincide_con_el_mac_ingenuo_del_mismo_par(self):
        clave, msg = b"secreta", b"pago 100"
        self.assertNotEqual(mac_ingenuo(clave, msg), mac_hmac(clave, msg))

class VerificarMac(unittest.TestCase):
    def setUp(self):
        self.tag = mac_hmac(b"secreta", b"pago 100")

    def test_acepta_el_tag_correcto(self):
        self.assertTrue(verificar_mac(self.tag, self.tag))

    def test_rechaza_un_solo_nibble_distinto(self):
        primero = "0" if self.tag[0] != "0" else "1"
        alterado = primero + self.tag[1:]
        self.assertFalse(verificar_mac(self.tag, alterado))

    def test_no_explota_con_largos_distintos_ni_con_no_ascii(self):
        self.assertFalse(verificar_mac(self.tag, ""))
        self.assertFalse(verificar_mac(self.tag, "ñ" * len(self.tag)))

if __name__ == "__main__":
    unittest.main(verbosity=2)
