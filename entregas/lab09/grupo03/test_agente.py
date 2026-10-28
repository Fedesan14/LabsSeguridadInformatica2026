"""Pruebas unitarias del loop del agente, sin red ni Docker."""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "src"))
import agente_esqueleto


class ClienteFinal:
    def paso(self, resultados):
        return {"tipo": "final", "texto": "listo"}


class ClienteUnaTool:
    def __init__(self):
        self.llamadas = 0
        self.resultado_recibido = None
    def paso(self, resultados):
        self.llamadas += 1
        if self.llamadas == 1:
            return {"tipo": "tool", "nombre": "http_get", "argumentos": {"url": "http://phantomcorp/"}, "id": "t-1"}
        self.resultado_recibido = resultados
        return {"tipo": "final", "texto": "listo"}


class LoopDeAgente(unittest.TestCase):
    def test_finaliza_sin_ejecutar_una_tool(self):
        with patch.object(agente_esqueleto, "crear_cliente", return_value=ClienteFinal()):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(agente_esqueleto.main(), 0)
        self.assertIn("Fin: listo", salida.getvalue())

    def test_realimenta_salida_e_identifica_flag(self):
        cliente = ClienteUnaTool()
        with patch.object(agente_esqueleto, "crear_cliente", return_value=cliente), patch.object(agente_esqueleto, "ejecutar_tool", return_value="ok FLAG{prueba}"):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(agente_esqueleto.main(), 0)
        self.assertEqual(cliente.resultado_recibido, [{"id": "t-1", "output": "ok FLAG{prueba}"}])
        self.assertIn("FLAG{prueba}", salida.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
