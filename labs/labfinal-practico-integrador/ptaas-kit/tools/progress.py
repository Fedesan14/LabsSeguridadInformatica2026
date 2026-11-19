#!/usr/bin/env python3
"""Autoevaluación de avance: tasks por change, Scenarios por spec y cantidad de tests.

    python tools/progress.py

No reemplaza la corrida de tests: informa dónde estás y qué falta.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENSPEC = ROOT / "openspec"
TASK_RE = re.compile(r"^\s*- \[( |x|X)\]", re.M)
SCENARIO_RE = re.compile(r"^### Scenario:", re.M)
TESTS_LINE_RE = re.compile(r"^Tests?:\s*(.+)$", re.M)


def changes_progress() -> list[tuple[str, int, int]]:
    rows = []
    for tasks in sorted((OPENSPEC / "changes").glob("*/tasks.md")):
        marks = TASK_RE.findall(tasks.read_text(encoding="utf-8"))
        rows.append((tasks.parent.name, sum(m.lower() == "x" for m in marks), len(marks)))
    return rows


def specs_summary() -> list[tuple[str, int, list[str]]]:
    rows = []
    for spec in sorted((OPENSPEC / "specs").glob("*/spec.md")):
        text = spec.read_text(encoding="utf-8")
        m = TESTS_LINE_RE.search(text)
        files = re.findall(r"tests/[\w./]+\.py", m.group(1)) if m else []
        rows.append((spec.parent.name, len(SCENARIO_RE.findall(text)), files))
    return rows


def count_tests() -> int | None:
    try:
        out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
                             cwd=ROOT, capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"(\d+) tests? collected", out) or re.search(r"^(\d+)/\d+ tests collected", out, re.M)
    return int(m.group(1)) if m else sum(1 for ln in out.splitlines() if "::" in ln)


def bar(done: int, total: int, width: int = 20) -> str:
    frac = done / total if total else 0
    return "█" * round(frac * width) + "░" * (width - round(frac * width)) + f" {done}/{total} ({frac:.0%})"


def main() -> int:
    print("== Tasks por change ==")
    for name, done, total in changes_progress():
        print(f"{name:42s} {bar(done, total)}")

    print("\n== Specs (Scenarios y archivos de test declarados) ==")
    missing = 0
    total_scn = 0
    for name, n, files in specs_summary():
        total_scn += n
        absent = [f for f in files if not (ROOT / f).exists()]
        flag = "" if files and not absent else "  ← falta línea 'Tests:' o archivo inexistente"
        missing += bool(flag)
        print(f"{name:22s} {n:3d} Scenarios  tests: {', '.join(files) or '—'}{flag}")
    print(f"{'TOTAL':22s} {total_scn:3d} Scenarios")

    n_tests = count_tests()
    print(f"\n== Tests recolectados: {n_tests if n_tests is not None else 'no disponible'} ==")
    if n_tests is not None and n_tests < total_scn:
        print(f"Atención: hay menos tests ({n_tests}) que Scenarios ({total_scn}).")
        missing += 1
    print("\nRecordá: tests verdes (`python -m pytest -q`) y evals (`python evals/run_evals.py --mode golden`).")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
