"""Reglas de parada de los loops agénticos (deterministas; el LLM propone, el harness decide)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoopDecision:
    decision: str      # "continue" | "stop"
    reason: str


def decide_recon(iteration: int, new_assets: int, max_iterations: int) -> LoopDecision:
    """Loop A: parar si el grafo se estabilizó o se alcanzó el tope."""
    if iteration >= max_iterations:
        return LoopDecision("stop", "tope de iteraciones alcanzado")
    if new_assets == 0:
        return LoopDecision("stop", "grafo estabilizado")
    return LoopDecision("continue", f"{new_assets} activos nuevos")


def decide_detection(history_new_evidence: list[int], max_iterations: int,
                     resolved: bool = False) -> LoopDecision:
    """Loop B: parar si se resolvió, tras 2 iteraciones sin evidencia nueva o al tope."""
    if resolved:
        return LoopDecision("stop", "hallazgo resuelto")
    if len(history_new_evidence) >= max_iterations:
        return LoopDecision("stop", "tope de iteraciones alcanzado")
    if len(history_new_evidence) >= 2 and all(n == 0 for n in history_new_evidence[-2:]):
        return LoopDecision("stop", "sin ganancia de información")
    return LoopDecision("continue", "hay evidencia nueva o iteraciones disponibles")


def decide_validation(attempts: int, evidence_sufficient: bool, max_attempts: int) -> LoopDecision:
    """Loop C: parar con evidencia suficiente o intentos agotados."""
    if evidence_sufficient:
        return LoopDecision("stop", "evidencia suficiente")
    if attempts >= max_attempts:
        return LoopDecision("stop", "intentos agotados")
    return LoopDecision("continue", "evidencia insuficiente")
