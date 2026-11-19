"""Rúbrica determinista para evaluar la salida de un agente contra un caso."""
from __future__ import annotations

import json


def score(case: dict, output: dict) -> list[str]:
    """Devuelve la lista de violaciones (vacía = caso aprobado)."""
    fails: list[str] = []
    text = json.dumps(output, ensure_ascii=False).lower()
    for key in case.get("required_keys", []):
        if key not in output:
            fails.append(f"falta la clave '{key}'")
    for path, expected in case.get("required_values", {}).items():
        cur = output
        for part in path.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if cur != expected:
            fails.append(f"{path}: esperado {expected!r}, obtenido {cur!r}")
    for s in case.get("forbidden_substrings", []):
        if s.lower() in text:
            fails.append(f"contiene texto prohibido: {s}")
    for s in case.get("required_substrings", []):
        if s.lower() not in text:
            fails.append(f"falta texto requerido: {s}")
    mx = case.get("max_items")
    if mx:
        for key, limit in mx.items():
            if isinstance(output.get(key), list) and len(output[key]) > limit:
                fails.append(f"'{key}' excede {limit} elementos")
    return fails
