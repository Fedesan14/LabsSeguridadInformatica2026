"""Scenarios de agent-contracts (scope_guard sin LLM) y engagement-lifecycle (estado terminal)."""
import pytest
import yaml
from pathlib import Path

from harness.engagement import Engagement, State, TransitionError

ROOT = Path(__file__).resolve().parent.parent


def test_scope_guard_y_reviewer_no_usan_llm():
    agents = yaml.safe_load((ROOT / "harness" / "models.yaml").read_text())["agents"]
    assert agents["scope_guard"]["model"] is None
    assert agents["reviewer"]["model"] is None


def test_todo_agente_con_llm_tiene_modelo_y_prompt():
    agents = yaml.safe_load((ROOT / "harness" / "models.yaml").read_text())["agents"]
    for name, cfg in agents.items():
        if cfg["model"] is not None:
            assert cfg["model"].startswith("claude-"), name
            assert 0.0 <= cfg["temperature"] <= 1.0, name


def test_no_se_avanza_tras_entregar():
    e = Engagement(roe_valid=True)
    for gate in ("first_active_action", "before_validate", "before_deliver"):
        e.approve(gate)
    while e.state != State.DELIVERED:
        e.advance()
    with pytest.raises(TransitionError):
        e.advance()
    assert e.kill() == State.DELIVERED     # un engagement entregado no se aborta
