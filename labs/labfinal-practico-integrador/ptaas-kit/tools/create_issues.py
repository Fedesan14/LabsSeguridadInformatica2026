#!/usr/bin/env python3
"""Genera un issue de GitHub por cada task pendiente de los changes 002 a 007.

    python tools/create_issues.py                          # solo muestra (no crea nada)
    python tools/create_issues.py --apply --repo ORG/REPO  # crea los issues con `gh`

Requiere GitHub CLI autenticado (`gh auth login`) y que existan los milestones
"Sprint 1", "Sprint 2" y "Sprint 3" y la etiqueta "task" en el repositorio.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGES = ROOT / "openspec" / "changes"
SPRINT = {"002": 1, "003": 1, "004": 2, "005": 2, "006": 3, "007": 3}
TASK_RE = re.compile(r"^\s*- \[ \]\s+(\d+\.\d+[a-z]?)\s+(.*)$")


def pending_tasks():
    for tasks in sorted(CHANGES.glob("*/tasks.md")):
        change = tasks.parent.name
        num = change.split("-")[0]
        if num not in SPRINT:
            continue
        for line in tasks.read_text(encoding="utf-8").splitlines():
            m = TASK_RE.match(line)
            if m:
                yield change, num, m.group(1), m.group(2).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="crear los issues (por defecto solo se muestran)")
    ap.add_argument("--repo", help="ORG/REPO (obligatorio con --apply)")
    args = ap.parse_args()
    if args.apply and not args.repo:
        ap.error("--apply requiere --repo ORG/REPO")

    count = 0
    for change, num, tid, text in pending_tasks():
        title = f"[{num} · {tid}] {text}"
        body = (f"Change: `openspec/changes/{change}/`\n"
                f"Task: {tid} — {text}\n\n"
                "Terminado cuando:\n- [ ] Hay Scenario (con caso negativo) y test\n"
                "- [ ] Tests, evals y `tools/progress.py` en verde\n- [ ] Revisado por otro integrante\n")
        cmd = ["gh", "issue", "create", "--repo", args.repo or "ORG/REPO", "--title", title,
               "--body", body, "--label", "task", "--milestone", f"Sprint {SPRINT[num]}"]
        count += 1
        if args.apply:
            subprocess.run(cmd, check=True)
        else:
            print(f"{title}   (Sprint {SPRINT[num]})")
    print(f"\n{count} issues {'creados' if args.apply else 'por crear (modo simulación, usá --apply)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
