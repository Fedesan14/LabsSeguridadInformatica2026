# Change 002 — Persistencia de la bitácora

## Por qué
La bitácora vive hoy en memoria. Sin persistencia no hay auditoría posible tras un reinicio, ni base para el informe ni para el tablero SDLC/ISO.

## Qué cambia
- Almacenamiento append-only en SQLite, un archivo por engagement.
- Verificador de integridad por línea de comandos.
- La cadena de hashes sobrevive a reinicios y se valida al abrir.

## Criterios de aceptación
1. Un registro escrito se recupera tras reiniciar el proceso.
2. Alterar o borrar una fila hace fallar `python -m harness.audit verify <archivo>`.
3. No existe API de actualización ni borrado de registros.

## Requisitos a escribir (semillas para el delta de `audit-log`)
- Persistencia por engagement y aislamiento entre engagements.
- Verificación al abrir y bajo demanda.
- Comportamiento ante una cadena corrupta: el engagement NO DEBE continuar.
- Escrituras concurrentes sin romper la cadena.

## Preguntas abiertas (completar en design.md)
- ¿Triggers de SQLite que impidan UPDATE/DELETE o solo convención?
- ¿Cómo se maneja el primer registro (GENESIS) por engagement?
- ¿Qué se guarda de la evidencia: referencia o contenido cifrado?
