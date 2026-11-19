"""Máquina de estados del engagement. Las transiciones con gate exigen aprobación humana."""
from __future__ import annotations

from enum import Enum


class State(str, Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    RECON = "RECON"
    CORRELATE = "CORRELATE"
    ANALYZE = "ANALYZE"
    VALIDATE = "VALIDATE"
    REPORT = "REPORT"
    DELIVERED = "DELIVERED"
    ABORTED = "ABORTED"


_NEXT = {
    State.CREATED: State.AUTHORIZED,
    State.AUTHORIZED: State.RECON,
    State.RECON: State.CORRELATE,
    State.CORRELATE: State.ANALYZE,
    State.ANALYZE: State.VALIDATE,
    State.VALIDATE: State.REPORT,
    State.REPORT: State.DELIVERED,
}
# Gate HITL: destino -> nombre de la aprobación requerida
_GATES = {
    State.RECON: "first_active_action",
    State.VALIDATE: "before_validate",
    State.DELIVERED: "before_deliver",
}


class TransitionError(Exception): ...


class Engagement:
    def __init__(self, roe_valid: bool):
        self.state = State.CREATED
        self.roe_valid = roe_valid
        self.approvals: set[str] = set()

    def approve(self, gate: str) -> None:
        self.approvals.add(gate)

    def advance(self) -> State:
        if self.state in (State.DELIVERED, State.ABORTED):
            raise TransitionError(f"estado terminal: {self.state}")
        target = _NEXT[self.state]
        if target == State.AUTHORIZED and not self.roe_valid:
            raise TransitionError("sin RoE válido no hay autorización")
        gate = _GATES.get(target)
        if gate and gate not in self.approvals:
            raise TransitionError(f"falta aprobación HITL: {gate}")
        self.state = target
        return self.state

    def kill(self) -> State:
        if self.state != State.DELIVERED:
            self.state = State.ABORTED
        return self.state
