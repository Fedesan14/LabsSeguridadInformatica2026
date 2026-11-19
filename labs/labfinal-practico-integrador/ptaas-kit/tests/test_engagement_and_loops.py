import pytest

from harness.engagement import Engagement, State, TransitionError
from harness.loops import decide_detection, decide_recon, decide_validation


def _avanzar_hasta(e: Engagement, destino: State):
    while e.state != destino:
        e.advance()


def test_sin_roe_no_se_autoriza():
    with pytest.raises(TransitionError):
        Engagement(roe_valid=False).advance()


def test_primera_accion_activa_requiere_gate():
    e = Engagement(roe_valid=True); e.advance()          # AUTHORIZED
    with pytest.raises(TransitionError):
        e.advance()
    e.approve("first_active_action")
    assert e.advance() == State.RECON


def test_validacion_y_entrega_requieren_aprobacion():
    e = Engagement(roe_valid=True); e.approve("first_active_action")
    _avanzar_hasta(e, State.ANALYZE)
    with pytest.raises(TransitionError):
        e.advance()
    e.approve("before_validate"); _avanzar_hasta(e, State.REPORT)
    with pytest.raises(TransitionError):
        e.advance()
    e.approve("before_deliver")
    assert e.advance() == State.DELIVERED


def test_kill_switch_aborta_desde_cualquier_estado_salvo_entregado():
    e = Engagement(roe_valid=True); e.advance()
    assert e.kill() == State.ABORTED
    with pytest.raises(TransitionError):
        e.advance()


def test_loop_a_grafo_estabilizado_y_tope():
    assert decide_recon(1, 0, 5).reason == "grafo estabilizado"
    assert decide_recon(5, 3, 5).reason == "tope de iteraciones alcanzado"
    assert decide_recon(2, 3, 5).decision == "continue"


def test_loop_b_sin_ganancia_de_informacion():
    d = decide_detection([2, 0, 0], max_iterations=4)
    assert d.decision == "stop" and d.reason == "sin ganancia de información"
    assert decide_detection([2, 1], 4).decision == "continue"
    assert decide_detection([1], 4, resolved=True).reason == "hallazgo resuelto"


def test_loop_c_topes():
    assert decide_validation(2, False, 2).reason == "intentos agotados"
    assert decide_validation(1, True, 2).reason == "evidencia suficiente"
