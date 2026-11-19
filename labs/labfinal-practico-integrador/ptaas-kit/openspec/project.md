# Proyecto: PTaaS (Pentest as a Service)

## Propósito
Plataforma de pentest **autorizado** orientada a swarm de agentes, alineada a PTES, NIST SP 800-115, OWASP WSTG/MASVS, OSSTMM, MITRE ATT&CK, CVSS v4.0, CWE e ISO/IEC 29147/30111.

## Stack
Python 3.12 · Pydantic v2 · LangGraph · MCP · pytest · mypy --strict · ruff · SQLite (MVP) → Postgres.

## Capabilities
authorization · asset-discovery · correlation · vuln-analysis · validation · reporting
(transversales) engagement-lifecycle · audit-log · tool-adapters · poc-catalog · agent-contracts

Las 11 capabilities viven en `openspec/specs/` (54 Scenarios). Trazabilidad spec → tests: `docs/enunciado-alumnos.md`.

## Convenciones
- Spec = fuente de verdad; deltas en `changes/`, estado estable en `specs/`.
- Requisitos con Scenarios Given/When/Then; un Scenario = un test.
- Ningún agente ejecuta herramientas directo: todo por `Harness.invoke`.
- Targets de desarrollo: laboratorio propio aislado (DVWA/Juice Shop).

## Fuera del MVP
Multi-tenant productivo, post-explotación avanzada, pivoting, generación autónoma de exploits.
