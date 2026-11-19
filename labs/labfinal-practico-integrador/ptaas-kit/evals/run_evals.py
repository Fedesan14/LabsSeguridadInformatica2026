#!/usr/bin/env python3
"""Evals por agente.

  python evals/run_evals.py --mode golden           # valida casos + rúbrica (offline, CI)
  python evals/run_evals.py --mode live --agent correlation   # llama al modelo (requiere API key)

El modo `live` NO fue probado en este kit: es un esqueleto para que el equipo lo complete.
Carga el prompt de prompts/ y el modelo de harness/models.yaml.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evals.rubric import score  # noqa: E402

PROMPT_FILES = {
    "orchestrator": "00-orchestrator.md", "correlation": "03-correlation.md",
    "validation": "05-validation.md", "vuln_analysis": "04-vuln-analysis.md",
    "asset_discovery": "02-asset-discovery.md", "reporting": "06-reporting.md",
}


def load_cases(agent: str | None = None) -> list[dict]:
    cases = []
    for f in sorted((ROOT / "evals" / "cases").glob("*.json")):
        cases += json.loads(f.read_text(encoding="utf-8"))
    return [c for c in cases if agent in (None, c["agent"])]


def run_golden(cases: list[dict]) -> dict[str, list[str]]:
    return {c["id"]: score(c, c["golden_output"]) for c in cases}


def run_live(cases: list[dict]) -> dict[str, list[str]]:
    import anthropic  # pip install anthropic

    models = yaml.safe_load((ROOT / "harness" / "models.yaml").read_text())["agents"]
    client = anthropic.Anthropic()
    results = {}
    for c in cases:
        cfg = models[c["agent"]]
        system = (ROOT / "prompts" / PROMPT_FILES[c["agent"]]).read_text(encoding="utf-8")
        msg = client.messages.create(
            model=cfg["model"], max_tokens=cfg["max_tokens"], temperature=cfg["temperature"],
            system=system + "\nRespondé únicamente con JSON válido.",
            messages=[{"role": "user", "content": json.dumps(c["input"], ensure_ascii=False)}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "text", None))
        try:
            out = json.loads(text)
        except json.JSONDecodeError:
            results[c["id"]] = ["la salida no es JSON válido"]
            continue
        results[c["id"]] = score(c, out)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["golden", "live"], default="golden")
    ap.add_argument("--agent")
    args = ap.parse_args()
    cases = load_cases(args.agent)
    results = run_golden(cases) if args.mode == "golden" else run_live(cases)
    failed = {k: v for k, v in results.items() if v}
    for k, v in results.items():
        print(("FAIL " if v else "PASS ") + k, *v, sep=" | " if v else "")
    print(f"\n{len(results) - len(failed)}/{len(results)} casos aprobados")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
