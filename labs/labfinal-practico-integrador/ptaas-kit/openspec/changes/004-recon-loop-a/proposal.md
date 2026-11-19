# Change 004 — Recon real y loop A integrado

## Por qué
El loop A (relevamiento) existe como regla de parada, pero no hay adaptadores reales ni un orquestador que lo ejecute contra el laboratorio.

## Qué cambia
- Adaptadores `subfinder.enum` y `httpx.probe` con salida validada por schema.
- Persistencia del `AssetGraph`.
- Orquestación del loop A (Recon ↔ Correlación) pasando siempre por `Harness.invoke`.

## Criterios de aceptación
1. El loop A corre contra el laboratorio y termina por "grafo estabilizado" o por tope.
2. Todo descubrimiento fuera de alcance queda registrado como tal y **no se sondea**.
3. Cada invocación aparece en la bitácora con su token.
4. Los adaptadores se prueban con fixtures; la corrida real es solo contra el lab.

## Requisitos a escribir (semillas para `asset-discovery` y `tool-adapters`)
- Esquema de salida de cada adaptador y rechazo de salidas inválidas.
- Normalización de activos y deduplicación en el grafo.
- Orden pasivo → activo y respeto del rate limit.
- Manejo de errores de herramienta (timeout, binario ausente) sin romper el engagement.

## Preguntas abiertas (completar en design.md)
- ¿Cómo se versiona el `AssetGraph` entre iteraciones?
- ¿Qué hace el orquestador si una herramienta devuelve datos parciales?
- ¿Cuándo se promueve un hallazgo de recon a candidato de correlación?
