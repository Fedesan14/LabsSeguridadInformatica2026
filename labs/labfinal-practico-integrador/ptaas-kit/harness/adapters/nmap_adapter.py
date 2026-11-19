"""Adaptador nmap.service_scan: detección de servicios acotada y sin scripts."""
from __future__ import annotations

from harness.adapters.common import (Runner, default_runner, load_profiles,
                                     reject_forbidden, validate_target)
from harness.contracts import Action, Phase, ScopeToken


def build_argv(target: str, profile: dict | None = None) -> list[str]:
    p = profile or load_profiles()["nmap"]
    t = validate_target(target, allow_cidr=True)
    argv = [p["binary"], *p["fixed_args"], "--max-rate", str(p["max_rate_pps"]),
            "-oX", "-", t]
    reject_forbidden(argv, p["forbidden_args"])
    return argv


class NmapServiceScan:
    name = "nmap.service_scan"
    allowed_phases = (Phase.RECON,)
    destructive = False

    def __init__(self, runner: Runner = default_runner, profile: dict | None = None):
        self._runner = runner
        self._profile = profile or load_profiles()["nmap"]

    def run(self, action: Action, target: str, token: ScopeToken) -> dict:
        argv = build_argv(target, self._profile)
        raw = self._runner(argv, self._profile["timeout_s"])
        return {"tool": "nmap", "target": target, "format": "xml", "raw": raw}
