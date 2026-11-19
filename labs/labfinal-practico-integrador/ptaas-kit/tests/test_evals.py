"""Las evals golden deben pasar, y la rúbrica debe poder FALLAR (si no, no mide nada)."""
from evals.rubric import score
from evals.run_evals import load_cases, run_golden


def test_todos_los_casos_golden_pasan():
    res = run_golden(load_cases())
    assert len(res) >= 10
    assert {k: v for k, v in res.items() if v} == {}


def test_hay_casos_para_los_agentes_con_llm_criticos():
    agentes = {c["agent"] for c in load_cases()}
    assert {"orchestrator", "correlation", "validation", "vuln_analysis"} <= agentes


def test_la_rubrica_detecta_una_salida_mala():
    caso = next(c for c in load_cases() if c["id"] == "val-001-solo-catalogo")
    mala = {"poc_id": "POC-NEW-1", "parameters": {"payload": "<script>"}}
    fallas = score(caso, mala)
    assert any("poc_id" in f for f in fallas) and any("prohibido" in f for f in fallas)


def test_la_rubrica_detecta_cve_inventado():
    caso = next(c for c in load_cases() if c["id"] == "corr-001-sin-cve-no-inventa")
    assert score(caso, {"candidates": [{"cve": "CVE-2020-9999"}]})
