---
name: ptes-reporting
description: Usar al generar o diseñar el informe de hallazgos de PTaaS: mapeo CWE, scoring CVSS v4.0, EPSS, ATT&CK, remediación y divulgación ISO/IEC 29147.
---

# Reporte de hallazgos

## Campos obligatorios por hallazgo
- ID, título, activo afectado, fase/herramienta de origen
- **CWE** (taxonomía) y, si aplica, CVE
- **CVSS v4.0** (vector + puntaje) y **EPSS** (probabilidad) para priorizar
- Técnica **MITRE ATT&CK** relacionada (si aplica)
- Evidencia (referencia a bitácora y artefactos del sandbox)
- Estado de validación: no validado / validado en sandbox (aprobado por Reviewer)
- Remediación recomendada y referencia (OWASP WSTG / NIST SP 800-115)

## Estructura del informe (PTES §7)
1. Resumen ejecutivo (impacto de negocio, no jerga)
2. Alcance y RoE (ventana, activos, exclusiones)
3. Metodología (PTES, NIST 800-115, WSTG)
4. Hallazgos priorizados
5. Anexos: bitácora de acciones, inventario de activos

## Reglas
- Sin hallazgo sin CWE + CVSS + remediación (criterio de aceptación del MVP).
- No incluir datos sensibles del cliente en claro; redactar evidencia.
- Divulgación y manejo según ISO/IEC 29147 / 30111; entrega solo tras gate HITL.
