"""Pruebas del recolector sin Docker ni red externa."""
import os
import sys
import unittest
from unittest.mock import patch

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "src"))
import recolector


class BuscarFlagTests(unittest.TestCase):
    def test_encuentra_flag_y_corta_el_recorrido(self):
        consultas = []
        def falsa_consulta(base, id_):
            consultas.append(id_)
            if id_ == 3:
                return {"id": id_, "legajo_oculto": "FLAG{automation_pays_off}"}
            return {"id": id_, "nombre": "normal"}
        with patch.object(recolector, "consultar_legajo", side_effect=falsa_consulta):
            hallazgo = recolector.buscar_flag("http://local", 1, 5)
        self.assertEqual(hallazgo, (3, "FLAG{automation_pays_off}"))
        self.assertEqual(consultas, [1, 2, 3])

    def test_omite_respuestas_invalidas(self):
        with patch.object(recolector, "consultar_legajo", return_value=None):
            self.assertIsNone(recolector.buscar_flag("http://local", 1, 2))

    def test_rechaza_intervalo_invertido(self):
        with self.assertRaises(ValueError):
            recolector.buscar_flag("http://local", 2, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
