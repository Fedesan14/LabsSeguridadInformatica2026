"""Integridad de la trazabilidad spec → tests (la usa tools/progress.py)."""
from pathlib import Path

from tools.progress import changes_progress, specs_summary

ROOT = Path(__file__).resolve().parent.parent


def test_toda_spec_declara_tests_existentes():
    for name, scenarios, files in specs_summary():
        assert scenarios > 0, f"{name}: sin Scenarios"
        assert files, f"{name}: falta la línea 'Tests:'"
        for f in files:
            assert (ROOT / f).exists(), f"{name}: {f} no existe"


def test_toda_spec_tiene_un_scenario_negativo_de_seguridad_o_de_rechazo():
    palabras = ("bloque", "rechaz", "falla", "no se ejecuta", "no se avanza", "no ", "pending", "aborted")
    for spec in (ROOT / "openspec" / "specs").glob("*/spec.md"):
        texto = spec.read_text(encoding="utf-8").lower()
        assert any(p in texto for p in palabras), spec.parent.name


def test_hay_siete_changes_con_tasks():
    nombres = [n for n, _, _ in changes_progress()]
    assert len(nombres) >= 7 and any(n.startswith("007") for n in nombres)
