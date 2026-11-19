---
name: openspec-workflow
description: Usar al proponer, implementar o archivar cambios del proyecto PTaaS con OpenSpec (spec-driven). Aplica a cualquier cambio de comportamiento, nueva capability o tarea de tasks.md.
---

# OpenSpec workflow (PTaaS)

## Ciclo
1. **Propose**: crear `openspec/changes/<NNN-slug>/` con `proposal.md` (por qué + qué cambia), `design.md` (decisiones), `tasks.md` (checklist) y `specs/<capability>/spec.md` (deltas).
2. **Review**: detenerse y pedir validación humana del delta antes de codear.
3. **Implement**: ejecutar `tasks.md` en orden; test primero por cada Scenario; marcar `[x]` al terminar.
4. **Archive**: al mergear, promover el delta a `openspec/specs/<capability>/spec.md`.

## Formato de requisito
```markdown
## Requirement: <nombre>
El sistema DEBE <comportamiento verificable>.

### Scenario: <caso>
- GIVEN <contexto>
- WHEN <acción>
- THEN <resultado observable>
```

## Reglas
- Un Scenario = un test (`tests/<capability>/test_<scenario>.py`).
- Verbos normativos: DEBE / NO DEBE / PUEDE.
- Todo requisito de seguridad (alcance, autorización, bitácora) lleva al menos un Scenario negativo (lo bloqueado).
- No implementar nada que no esté en una spec o delta aprobado.
- Capabilities: authorization, asset-discovery, correlation, vuln-analysis, validation, reporting.
