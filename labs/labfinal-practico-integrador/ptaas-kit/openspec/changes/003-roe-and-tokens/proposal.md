# Change 003 — RoE y emisión de scope tokens

## Por qué
Hoy los tokens se construyen a mano en los tests. El sistema necesita convertir un **RoE firmado** en tokens de corta vida y por fase, y rechazar RoE peligrosos o incompletos antes de que exista cualquier token.

## Qué cambia
- Formato de RoE en YAML con alcance, ventana, exclusiones, contactos de emergencia y aprobador.
- Parser con validaciones fuertes.
- Emisor de tokens por fase con el TTL de `policy.yaml`.

## Criterios de aceptación
1. Un RoE válido produce un token solo para la fase pedida y dentro de la ventana.
2. Un RoE sin alcance, con ventana invertida o con CIDR no permitido se rechaza con un error explicativo.
3. Ninguna ruta del código crea `ScopeToken` fuera del emisor.

## Requisitos a escribir (semillas para el delta de `authorization`)
- Campos obligatorios del RoE y sus validaciones.
- Alcance máximo permitido en el laboratorio (`targets` de `profiles.yaml`).
- Exclusiones del RoE que prevalecen sobre el alcance.
- Expiración y no renovación automática.
- Registro en bitácora de cada emisión y rechazo.

## Preguntas abiertas (completar en design.md)
- ¿Cómo se representa la aprobación del RoE (firma, hash, aprobador)?
- ¿Qué pasa con un token si el RoE se revoca durante el engagement?
- ¿Se permiten tokens de múltiples fases en paralelo?
