import pytest

from harness.schemas import (Asset, CandidateFinding, PrioritizedVuln, SchemaError,
                             SchemaGate, dedupe, priority_score)


def test_activo_sin_herramienta_de_origen_se_rechaza():
    with pytest.raises(SchemaError):
        Asset("a1", "host", "10.0.0.5", source_tool="")


def test_candidato_sin_evidencia_se_rechaza():
    with pytest.raises(SchemaError):
        CandidateFinding("f1", "a1", cwe="CWE-79")


def test_dato_ausente_queda_como_null_o_unknown():
    c = CandidateFinding("f1", "a1", evidence_refs=["e1"])
    assert c.cve is None and c.epss is None and c.cwe == "unknown"


def test_dedupe_fusiona_evidencia():
    a = CandidateFinding("f1", "a1", cve="CVE-2024-0001", evidence_refs=["nvd"])
    b = CandidateFinding("f2", "a1", cve="CVE-2024-0001", evidence_refs=["zap"])
    out = dedupe([a, b])
    assert len(out) == 1 and out[0].evidence_refs == ["nvd", "zap"]


def test_vuln_sin_rationale_se_rechaza():
    with pytest.raises(SchemaError):
        PrioritizedVuln("f1", "confirmed", rationale="  ")


def test_priorizacion_reproducible_y_sensible_a_epss():
    a = priority_score(7.5, 0.3, 4)
    assert a == priority_score(7.5, 0.3, 4)
    assert priority_score(7.5, 0.9, 4) > a
    with pytest.raises(SchemaError):
        priority_score(11, None, 3)


def test_schema_invalido_dos_veces_escala_a_hitl():
    g = SchemaGate()
    assert g.record(False) == "RETRY"
    assert g.record(False) == "PENDING_HITL"
    assert SchemaGate().record(True) == "OK"
