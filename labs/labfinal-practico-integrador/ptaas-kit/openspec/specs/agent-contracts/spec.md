# Spec — agent-contracts

Tests: `tests/test_schemas.py`, `tests/test_evals.py`
Datos: `harness/models.yaml`, `prompts/`, `evals/`

## Requirement: Salida con schema
Toda salida de un agente hacia otro DEBE validar contra un schema tipado; el texto libre NO DEBE circular entre agentes.

### Scenario: activo sin herramienta de origen
- GIVEN un activo sin `source_tool`
- WHEN se intenta incorporar al grafo
- THEN se rechaza por schema inválido

## Requirement: Escalado ante salidas inválidas
Tras dos salidas inválidas consecutivas el sistema DEBE escalar a HITL y NO DEBE reintentar.

### Scenario: dos fallos seguidos
- GIVEN dos respuestas consecutivas que no validan
- WHEN se evalúa la segunda
- THEN el estado es PENDING_HITL

## Requirement: Priorización determinista
La prioridad DEBE calcularse de forma reproducible a partir de CVSS v4, EPSS y criticidad del activo.

### Scenario: mismos insumos
- GIVEN insumos idénticos
- WHEN se calcula dos veces
- THEN el resultado es el mismo

## Requirement: Scope Guard sin LLM
La autorización DEBE ser código determinista y NO DEBE delegarse a un modelo.

### Scenario: configuración de modelos
- GIVEN `harness/models.yaml`
- WHEN se revisa el agente `scope_guard`
- THEN su modelo es `null`

## Requirement: Evals ante cambios
Todo cambio de modelo o de prompt DEBE ir acompañado de la corrida de evals del agente afectado.

### Scenario: casos golden
- GIVEN el conjunto de casos de `evals/cases/`
- WHEN corre `run_evals.py --mode golden`
- THEN todos los casos pasan

### Scenario: la rúbrica detecta una salida mala
- GIVEN una salida con un PoC inventado o un CVE inexistente
- WHEN se evalúa con la rúbrica
- THEN se reportan violaciones
