# Entregable — Lab Extra 5: JWT inseguro

> Copiá este archivo a `entregas/labextra5/grupoXX/informe.md` y completalo.

**Grupo:** XX · **Integrantes:** (apellido, nombre — usuario de GitHub)

**Declaración de uso de IA:** (obligatoria)

---

## 1. Anatomía del token real

Pegá el token que obtuviste del login y, debajo, su header y payload
decodificados (con tu `jwt_tool.py`). Marcá el claim problemático (R1).

## 2. Crack offline del secreto

- ¿Cómo verificaste cada candidato **sin tocar el servidor**? Explicá el
  oráculo en una oración y pegá el código de `firma_es_valida()`.
- Secreto encontrado y cuántos candidatos probaste.
- ¿Cuánto tardó? ¿Qué cambiaría con un secreto de 32 bytes aleatorios?

## 3. Las dos forjas

### R2 — Escalada vertical (role=admin)
- Token forjado + respuesta de `/admin` con la flag.
- Diff conceptual: ¿qué cambiaste respecto del token original?

### R3 — Suplantación horizontal (sub=maria)
- Token forjado + respuesta de `/perfil` con la flag.
- ¿Por qué esto es un IDOR aunque no hay `?id=`?

## 4. Control de sanidad

Mostrá que el servidor **sí rechaza**: (a) el token real de diego en `/admin`
(403), (b) tu token forjado con UN carácter cambiado en la firma (401).

## 5. Preguntas P1–P5

(Desarrollá las 5 del README.)

## 6. Evidencia de progreso

Captura de `./ctf status extra5` con los 3 ✓ + `evidencia/` según protocolo.
