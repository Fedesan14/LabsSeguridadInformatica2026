import time

import pytest

from harness.contracts import (Action, AuditLog, Guard, Harness, KillSwitch, Phase,
                               ScopeToken)
from harness.policy_loader import phase_allowlist


class FakeAdapter:
    def __init__(self, name, phases, destructive=False):
        self.name, self.allowed_phases, self.destructive = name, phases, destructive
        self.calls = []

    def run(self, action, target, token):
        self.calls.append(target)
        return {"ok": True, "target": target}


def make_token(phase=Phase.RECON, cidrs=("10.0.0.0/24",), domains=("lab.example.test",),
               start=None, end=None):
    now = time.time()
    return ScopeToken("eng-1", cidrs, domains,
                      now - 5 if start is None else start,
                      now + 600 if end is None else end, phase)


@pytest.fixture
def token():
    return make_token()


@pytest.fixture
def env():
    guard = Guard(phase_allowlist())
    audit = AuditLog()
    ks = KillSwitch()
    adapters = {
        "httpx.probe": FakeAdapter("httpx.probe", (Phase.RECON,)),
        "zap.baseline_scan": FakeAdapter("zap.baseline_scan", (Phase.ANALYZE,)),
        "poc_catalog.run_parametrized": FakeAdapter("poc_catalog.run_parametrized",
                                                    (Phase.VALIDATE,)),
    }
    return Harness(guard, audit, adapters, ks), guard, audit, ks, adapters


def act(name, phase, **kw):
    return Action(name, phase, **kw)
