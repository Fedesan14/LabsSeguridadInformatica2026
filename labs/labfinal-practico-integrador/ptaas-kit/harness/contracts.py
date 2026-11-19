"""Contratos del harness PTaaS (esqueleto). El contrato, no el exploit.

Invariantes:
  I1. Toda acción que toca un activo pasa por Harness.invoke.
  I2. El Guard es determinista (sin LLM).
  I3. Toda decisión (OK, BLOCKED, PENDING_HITL, ABORTED) queda en bitácora.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Phase(str, Enum):
    RECON = "recon"
    CORRELATE = "correlate"
    ANALYZE = "analyze"
    VALIDATE = "validate"
    REPORT = "report"


class Result(str, Enum):
    OK = "OK"
    BLOCKED = "BLOCKED"
    PENDING_HITL = "PENDING_HITL"
    ABORTED = "ABORTED"


class ScopeViolation(Exception): ...
class KillSwitchEngaged(Exception): ...


@dataclass(frozen=True)
class ScopeToken:
    engagement_id: str
    allowed_cidrs: tuple[str, ...]
    allowed_domains: tuple[str, ...]
    window_start: float
    window_end: float
    phase: Phase

    def is_live(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        return self.window_start <= now <= self.window_end


@dataclass(frozen=True)
class Action:
    name: str                      # capability declarada, p.ej. "httpx.probe"
    phase: Phase
    destructive: bool = False
    requires_human_approval: bool = False


class ToolAdapter(Protocol):
    name: str
    allowed_phases: tuple[Phase, ...]
    destructive: bool

    def run(self, action: Action, target: str, token: ScopeToken) -> dict:
        """Debe devolver JSON parseable. Nunca ejecuta fuera de `target`."""
        ...


class Guard:
    """Autorización determinista. Sin LLM, sin heurísticas."""

    def __init__(self, phase_allowlist: dict[Phase, set[str]], approvals: set[str] | None = None):
        self.phase_allowlist = phase_allowlist
        self._approvals = approvals or set()

    def approve(self, action_name: str, target: str) -> None:
        self._approvals.add(f"{action_name}@{target}")

    def approved(self, action: Action, target: str) -> bool:
        return f"{action.name}@{target}" in self._approvals

    def is_allowed(self, action: Action, target: str, token: ScopeToken) -> bool:
        if action.destructive:        # acciones destructivas prohibidas en el MVP
            return False
        if action.phase != token.phase:
            return False
        if action.name not in self.phase_allowlist.get(token.phase, set()):
            return False
        return self._in_scope(target, token)

    @staticmethod
    def _in_scope(target: str, token: ScopeToken) -> bool:
        try:
            ip = ipaddress.ip_address(target)
            return any(ip in ipaddress.ip_network(c) for c in token.allowed_cidrs)
        except ValueError:
            host = target.lower().rstrip(".")
            return any(
                host == d or host.endswith("." + d) for d in token.allowed_domains
            )


@dataclass
class AuditLog:
    """Append-only con hash encadenado (detecta manipulación)."""

    entries: list[dict] = field(default_factory=list)

    def record(self, agent: str, action: Action, target: str,
               token: ScopeToken, result: Result) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else "GENESIS"
        body = {
            "ts": time.time(), "engagement": token.engagement_id, "agent": agent,
            "action": action.name, "target": target, "phase": token.phase.value,
            "result": result.value, "prev": prev,
        }
        body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        self.entries.append(body)
        return body


class KillSwitch:
    engaged: bool = False


class Harness:
    def __init__(self, guard: Guard, audit: AuditLog,
                 tools: dict[str, ToolAdapter], killswitch: KillSwitch):
        self.guard, self.audit, self.tools, self.killswitch = guard, audit, tools, killswitch

    def invoke(self, agent: str, action: Action, target: str, token: ScopeToken) -> dict:
        if self.killswitch.engaged:
            self.audit.record(agent, action, target, token, Result.ABORTED)
            raise KillSwitchEngaged()
        if not token.is_live() or not self.guard.is_allowed(action, target, token):
            self.audit.record(agent, action, target, token, Result.BLOCKED)
            raise ScopeViolation(f"{action.name} sobre {target} fuera de RoE/ventana/fase")
        if action.requires_human_approval and not self.guard.approved(action, target):
            self.audit.record(agent, action, target, token, Result.PENDING_HITL)
            return {"status": "PENDING_HITL"}
        adapter = self.tools.get(action.name)
        if adapter is None:
            self.audit.record(agent, action, target, token, Result.BLOCKED)
            raise ScopeViolation(f"capability sin adaptador registrado: {action.name}")
        if token.phase not in adapter.allowed_phases:
            self.audit.record(agent, action, target, token, Result.BLOCKED)
            raise ScopeViolation(f"adaptador {adapter.name} no habilitado en {token.phase}")
        out = adapter.run(action, target, token)
        self.audit.record(agent, action, target, token, Result.OK)
        return out
