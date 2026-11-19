"""Adaptador nuclei.safe_templates: solo templates curados y tags permitidos."""
from __future__ import annotations

from harness.adapters.common import (Runner, default_runner, load_profiles,
                                     validate_url)
from harness.contracts import Action, Phase, ScopeToken


def build_argv(url: str, profile: dict | None = None) -> list[str]:
    p = profile or load_profiles()["nuclei"]
    u = validate_url(url)
    argv = [
        p["binary"], "-u", u,
        "-t", p["templates_dir"],
        "-tags", ",".join(p["include_tags"]),
        "-etags", ",".join(p["exclude_tags"]),
        "-rate-limit", str(p["rate_limit_rps"]),
        *p["fixed_args"],
    ]
    # Invariante: ninguna etiqueta incluida puede estar también excluida o ser intrusiva.
    overlap = set(p["include_tags"]) & set(p["exclude_tags"])
    if overlap:
        raise ValueError(f"tags incluidas y excluidas a la vez: {sorted(overlap)}")
    return argv


class NucleiSafeTemplates:
    name = "nuclei.safe_templates"
    allowed_phases = (Phase.ANALYZE,)
    destructive = False

    def __init__(self, runner: Runner = default_runner, profile: dict | None = None):
        self._runner = runner
        self._profile = profile or load_profiles()["nuclei"]

    def run(self, action: Action, target: str, token: ScopeToken) -> dict:
        argv = build_argv(target, self._profile)
        raw = self._runner(argv, self._profile["timeout_s"])
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        return {"tool": "nuclei", "target": target, "format": "jsonl", "lines": lines}
