# Delta — asset-discovery

Tests: tests/test_engagement_and_loops.py

## Requirement: Relevamiento solo dentro de alcance
El sistema DEBE descubrir únicamente activos cubiertos por el scope token vigente; todo descubrimiento fuera de alcance DEBE registrarse como "fuera de alcance" sin ser tocado.

### Scenario: subdominio fuera de alcance
- GIVEN un token que autoriza `lab.example.test`
- WHEN el recon descubre `otro.ejemplo.org` como referencia
- THEN el activo se registra como "fuera de alcance", no se sondea y queda en bitácora

## Requirement: Pasivo antes que activo
El sistema DEBERÍA agotar técnicas pasivas antes de lanzar técnicas activas sobre un activo.

### Scenario: orden de técnicas
- GIVEN un dominio autorizado sin inventario previo
- WHEN comienza el relevamiento
- THEN las capabilities pasivas se ejecutan antes que las activas

## Requirement: Modelo de grafo de activos
El sistema DEBE producir un `AssetGraph` con, por activo: id, tipo, dirección, tecnologías detectadas y herramienta de origen.

### Scenario: activo sin herramienta de origen
- GIVEN un activo propuesto sin `source_tool`
- WHEN se intenta incorporarlo al grafo
- THEN se rechaza por schema inválido

## Requirement: Loop de relevamiento acotado
El loop A DEBE detenerse cuando no aparezcan activos nuevos o al alcanzar el tope de iteraciones de `policy.yaml`.

### Scenario: sin activos nuevos
- GIVEN una iteración que no agrega activos al grafo
- WHEN el agente evalúa continuar
- THEN `LoopDecision` es `stop` con motivo "grafo estabilizado"

### Scenario: tope alcanzado
- GIVEN que se llegó a `max_loop_iterations.recon`
- WHEN el agente propone otra iteración
- THEN el harness la rechaza y el engagement avanza de fase

## Requirement: Respeto del rate limit
El sistema NO DEBE superar `rate_limit_rps_per_target`.

### Scenario: ráfaga de sondeos
- GIVEN un límite de 5 rps por target
- WHEN el adaptador intenta emitir más de 5 solicitudes por segundo
- THEN el adaptador se auto-limita y no excede el umbral
