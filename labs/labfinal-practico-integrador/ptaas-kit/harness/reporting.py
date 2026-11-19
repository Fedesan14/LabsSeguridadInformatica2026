"""Generación del informe: exige CWE + CVSS v4 + remediación por hallazgo y gate de entrega."""
from __future__ import annotations

import re
from dataclasses import dataclass

CVSS4_RE = re.compile(
    r"^CVSS:4\.0/AV:[NALP]/AC:[LH]/AT:[NP]/PR:[NLH]/UI:[NPA]"
    r"/VC:[HLN]/VI:[HLN]/VA:[HLN]/SC:[HLN]/SI:[HLN]/SA:[HLN](/.+)?$"
)


class MissingField(ValueError): ...
class DeliveryNotApproved(Exception): ...


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    asset: str
    cwe: str
    cvss_v4_vector: str
    remediation: str
    validation_status: str       # "validated" | "not_validated"
    evidence_refs: tuple[str, ...] = ()
    epss: float | None = None


def _check(f: Finding) -> None:
    if not f.cwe or not re.match(r"^CWE-\d+$", f.cwe):
        raise MissingField(f"{f.id}: falta CWE válido")
    if not CVSS4_RE.match(f.cvss_v4_vector or ""):
        raise MissingField(f"{f.id}: falta vector CVSS v4.0 válido")
    if not f.remediation.strip():
        raise MissingField(f"{f.id}: falta remediación")


def render_report(engagement_id: str, findings: list[Finding]) -> dict:
    for f in findings:
        _check(f)
    lines = [f"# Informe de pentest — {engagement_id}", ""]
    for f in findings:
        estado = "validado en sandbox" if f.validation_status == "validated" else "no validado"
        lines += [f"## {f.id} — {f.title}", f"- Activo: {f.asset}", f"- {f.cwe} · {f.cvss_v4_vector}",
                  f"- Estado: {estado}", f"- Remediación: {f.remediation}", ""]
    return {"engagement_id": engagement_id, "markdown": "\n".join(lines),
            "findings": [f.id for f in findings], "delivered": False}


def deliver(report: dict, reviewer_approved: bool) -> dict:
    if not reviewer_approved:
        raise DeliveryNotApproved("la entrega requiere aprobación del Reviewer")
    return {**report, "delivered": True}
