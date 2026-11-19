#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pruebas de la receta, el ataque y la lectura de entradas inválidas."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cracker

AQUI = Path(__file__).resolve().parent
CASO = AQUI.parents[2] / "labs/labextra4-cracking/caso"


class PruebasCracker(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="labextra4-test-")
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "entrada.txt"

    def test_md5_y_sha256_vectores_publicados(self):
        # RFC 1321 y FIPS 180-4: mensaje 'abc', repartido entre salt y clave.
        self.assertEqual(cracker.hash_de("md5", "61", "bc"), "900150983cd24fb0d6963f7d28e17f72")
        self.assertEqual(cracker.hash_de("sha256", "61", "bc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_pbkdf2_vector_rfc7914_seccion11(self):
        # El primer bloque de dkLen=64 coincide con dkLen=32.
        with patch.object(cracker, "ITER_PBKDF2", 80_000):
            self.assertEqual(cracker.hash_de("pbkdf2", "4e61436c", "Password"),
                             "4ddcd8f60b98be21830cee5ef22701f9641a4418d04c0414aeff08876b34ab56")
        self.assertEqual(cracker.ITER_PBKDF2, 200_000)

    def test_sombra_bom_comentarios_y_hex_mayuscula(self):
        self.ruta.write_text("\ufeff# comentario\n\nusuario:md5:61:900150983CD24FB0D6963F7D28E17F72\n", encoding="utf-8")
        self.assertEqual(cracker.cargar_sombra(str(self.ruta)),
                         [("usuario", "md5", "61", "900150983cd24fb0d6963f7d28e17f72")])

    def test_sombra_rechaza_entradas_invalidas_con_numero_linea(self):
        filas = ["a:md5:61", "a:md5::" + "0" * 32,
                 "a:des:61:" + "0" * 32, "a:md5:6:" + "0" * 32,
                 "a:md5:zz:" + "0" * 32, "a:md5:61:" + "0" * 31,
                 "a:md5:61:" + "z" * 32]
        for fila in filas:
            with self.subTest(fila=fila):
                self.ruta.write_text("# comentario\n" + fila, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, r":2:"):
                    cracker.cargar_sombra(str(self.ruta))

    def test_sombra_rechaza_usuario_duplicado(self):
        fila = "u:md5:61:900150983cd24fb0d6963f7d28e17f72\n"
        self.ruta.write_text(fila * 2, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicado"):
            cracker.cargar_sombra(str(self.ruta))

    def test_reglas_y_deduplicacion(self):
        variantes = cracker.aplicar_reglas("phantom")
        for esperada in ("phantom", "phantom2024", "phantom2025", "phantom2026",
                         "phantom1", "phantom12", "phantom123", "Phantom", "Phantom2026"):
            self.assertIn(esperada, variantes)
        self.assertEqual(variantes, list(dict.fromkeys(variantes)))
        self.assertEqual(len(cracker.aplicar_reglas("123456")), 7)

    def test_diccionario_utf8_duplicados_y_espacios(self):
        self.ruta.write_text("contraseña\ncontraseña\n\n con espacios \n", encoding="utf-8")
        self.assertEqual(cracker.cargar_candidatos(str(self.ruta)), ["contraseña", " con espacios "])

    def test_caso_real_diccionario_reglas_y_loot(self):
        # El caso entregado es la referencia externa; no se regenera.
        sombra = [fila for fila in cracker.cargar_sombra(str(CASO / "sombra.txt")) if fila[0] != "root"]
        with contextlib.redirect_stdout(io.StringIO()):
            diccionario = cracker.crackear(sombra, str(CASO / "diccionario.txt"))
            reglas = cracker.crackear(sombra, str(CASO / "diccionario.txt"), True)
        self.assertEqual(diccionario, {"operador": "riverplate", "analista": "matecocido"})
        self.assertEqual(reglas, {**diccionario, "admin": "phantom2026"})
        for usuario, password in reglas.items():
            texto = cracker.descifrar_loot((CASO / "loot" / f"{usuario}.enc").read_text(), password)
            self.assertIn(f"Notas de {usuario} — CONFIDENCIAL", texto)
            self.assertIn("FLAG{", texto)

    def test_pbkdf2_se_prueba_y_no_se_omite(self):
        # Hash fijo de otra contraseña ficticia, con 200.000 iteraciones.
        self.ruta.write_text("incorrecta\nriverplate\n", encoding="utf-8")
        from hashlib import pbkdf2_hmac
        digest = pbkdf2_hmac("sha256", b"riverplate", b"salt-test", 200_000).hex()
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            resultado = cracker.crackear([("prueba", "pbkdf2", "73616c742d74657374", digest)], str(self.ruta))
        self.assertEqual(resultado, {"prueba": "riverplate"})
        self.assertIn("intentos=2", salida.getvalue())

    def test_diccionario_vacio_y_algoritmo_no_soportado(self):
        self.ruta.write_text("\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cracker.crackear([], str(self.ruta)), {})
        with self.assertRaises(ValueError):
            cracker.hash_de("des", "61", "bc")


if __name__ == "__main__":
    unittest.main(verbosity=2)
