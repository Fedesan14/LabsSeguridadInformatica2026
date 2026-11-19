"""Scenarios de la capability `authorization` (+ invariantes I1–I6 del harness)."""
import time

import pytest

from harness.contracts import KillSwitchEngaged, Phase, Result, ScopeViolation
from tests.conftest import act, make_token


def test_activo_fuera_de_alcance_se_bloquea_y_registra(env, token):
    h, _, audit, _, adapters = env
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("httpx.probe", Phase.RECON), "10.0.1.5", token)
    assert audit.entries[-1]["result"] == Result.BLOCKED.value
    assert audit.entries[-1]["target"] == "10.0.1.5"
    assert adapters["httpx.probe"].calls == []           # la herramienta nunca corrió


def test_activo_en_alcance_se_ejecuta_y_registra(env, token):
    h, _, audit, _, adapters = env
    out = h.invoke("recon", act("httpx.probe", Phase.RECON), "10.0.0.5", token)
    assert out["ok"] and adapters["httpx.probe"].calls == ["10.0.0.5"]
    assert audit.entries[-1]["result"] == Result.OK.value


def test_dominio_y_subdominio_en_alcance_pero_no_sufijo_enganoso(env, token):
    h, *_ = env
    h.invoke("recon", act("httpx.probe", Phase.RECON), "app.lab.example.test", token)
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("httpx.probe", Phase.RECON), "evil-lab.example.test", token)


def test_token_vencido_se_bloquea(env):
    h, _, audit, *_ = env
    vencido = make_token(start=time.time() - 100, end=time.time() - 10)
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("httpx.probe", Phase.RECON), "10.0.0.5", vencido)
    assert audit.entries[-1]["result"] == "BLOCKED"


def test_token_de_otra_fase_no_habilita_la_accion(env):
    h, *_ = env
    t_analyze = make_token(phase=Phase.ANALYZE)
    with pytest.raises(ScopeViolation):
        h.invoke("analysis", act("poc_catalog.run_parametrized", Phase.VALIDATE), "10.0.0.5", t_analyze)


def test_sondeo_en_fase_correlate_se_bloquea(env):
    h, *_ = env
    t = make_token(phase=Phase.CORRELATE)
    with pytest.raises(ScopeViolation):
        h.invoke("correlation", act("httpx.probe", Phase.RECON), "10.0.0.5", t)


def test_accion_fuera_de_allowlist_de_la_fase(env, token):
    h, *_ = env
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("masscan.sweep", Phase.RECON), "10.0.0.5", token)


def test_accion_destructiva_siempre_bloqueada(env, token):
    h, *_ = env
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("httpx.probe", Phase.RECON, destructive=True), "10.0.0.5", token)


def test_kill_switch_aborta_sin_ejecutar(env, token):
    h, _, audit, ks, adapters = env
    ks.engaged = True
    with pytest.raises(KillSwitchEngaged):
        h.invoke("recon", act("httpx.probe", Phase.RECON), "10.0.0.5", token)
    assert audit.entries[-1]["result"] == "ABORTED" and adapters["httpx.probe"].calls == []


def test_validacion_sin_aprobacion_queda_pending_hitl(env):
    h, guard, audit, _, adapters = env
    t = make_token(phase=Phase.VALIDATE)
    a = act("poc_catalog.run_parametrized", Phase.VALIDATE, requires_human_approval=True)
    out = h.invoke("validation", a, "10.0.0.5", t)
    assert out["status"] == "PENDING_HITL"
    assert audit.entries[-1]["result"] == "PENDING_HITL" and adapters[a.name].calls == []
    guard.approve(a.name, "10.0.0.5")
    assert h.invoke("validation", a, "10.0.0.5", t)["ok"]


def test_capability_sin_adaptador_se_bloquea(env, token, monkeypatch):
    h, guard, *_ = env
    guard.phase_allowlist[Phase.RECON].add("naabu.scan")
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("naabu.scan", Phase.RECON), "10.0.0.5", token)


def test_adaptador_no_habilitado_en_la_fase_se_bloquea(env, token):
    h, guard, _, _, adapters = env
    guard.phase_allowlist[Phase.RECON].add("zap.baseline_scan")
    with pytest.raises(ScopeViolation):
        h.invoke("recon", act("zap.baseline_scan", Phase.RECON), "10.0.0.5", token)
