# Entregable — Lab Extra 2: El repo que delata

> Copiá este archivo a `entregas/labextra2/grupoXX/informe.md` y completalo.

**Grupo:** XX · **Integrantes:** (apellido, nombre — usuario de GitHub)

**Declaración de uso de IA:** (obligatoria)

---

## 1. Línea de tiempo de la filtración

Tabla cronológica de TODOS los eventos relevantes de la historia (incluí los
commits "legítimos" también: el contexto es parte del informe):

| Fecha | Autor | Commit (hash corto) | Qué pasó | ¿Expone algo? |
|---|---|---|---|---|
| | | | | |

## 2. Hallazgos

### R1 — Secreto en commit viejo
- Comando(s) exacto(s):
- Salida relevante (pegá el diff):
- Qué secreto se expuso y qué habilita:

### R2 — Commit "perdido"
- Comando(s) exacto(s):
- ¿Cómo llegaste del reflog/fsck al contenido del objeto?
- Qué secreto se expuso:

### R3 — Rama abandonada
- Comando(s) exacto(s):
- Qué secreto se expuso:

## 3. Evaluación de exposición

Si este repo hubiera estado **público en GitHub** desde el commit inicial:
¿cuál de los 3 secretos habría sido encontrado primero por un bot? ¿Por qué?
¿Cuánto tiempo estimás que tardaría?

## 4. Plan de remediación (respondiendo P4)

Ordená y justificá: rotación de secretos, reescritura de historia, contacto a
quienes forkearon/clonaron, revocación de accesos, lecciones aprendidas.

## 5. Preguntas P1–P5

(Desarrollá las 5 preguntas del README.)

## 6. Evidencia de progreso

- Captura de `./ctf status extra2` con los 3 ✓.
- Confirmá que adjuntaste `evidencia/comandos.txt` y `evidencia/salidas/`
  (ver README § Reporte y evidencia).
