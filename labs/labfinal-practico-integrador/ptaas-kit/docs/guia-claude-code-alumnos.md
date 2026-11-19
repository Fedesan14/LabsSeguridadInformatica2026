# Guía: cómo trabajar con Claude Code en este proyecto

## Resumen
Claude Code es tu par de programación, no tu autoridad. El proyecto está armado para que **la spec y los tests lo mantengan honesto**: él propone, vos verificás. Si no podés explicar por qué funciona algo que escribió, no se commitea.

## Rutina diaria (≈ 2 h)
1. **Arrancar (10 min):** `git pull`, `python -m pytest -q`, `python tools/progress.py`. Elegir el task del día en `tasks.md`.
2. **Spec (25 min):** pedirle al agente `spec-author` el delta. Vos lo revisás: ¿hay Scenario **negativo**?
3. **Test primero (25 min):** que escriba el test que falla. Corrélo y confirmá que **falla por la razón correcta**.
4. **Implementar (40 min):** que haga pasar el test con el cambio mínimo.
5. **Revisar (15 min):** agente `security-reviewer` sobre el diff. Resolvé o justificá cada punto.
6. **Cerrar (5 min):** tests y evals verdes, `tasks.md` actualizado, commit referenciando el task.

## Plantillas de prompts

**Proponer un change**
> Usá el skill openspec-workflow. Escribí el delta de spec para `<capability>` cubriendo `<objetivo>`. Incluí al menos un Scenario negativo de seguridad por Requirement. No escribas código. Listá las preguntas abiertas.

**Test primero**
> Escribí solo los tests de los Scenarios del delta `<ruta>`. Deben fallar hoy. Mostrame cómo los corrés y por qué fallan.

**Implementar**
> Implementá lo mínimo para que pasen esos tests. No toques `harness/contracts.py` salvo que el delta lo pida. Respetá el skill harness-invariants.

**Revisión adversarial**
> Actuá como security-reviewer. Buscá caminos que eviten Harness.invoke, registros faltantes en la bitácora y entradas que lleguen al adaptador sin validar. Dame archivo:línea y un test que lo demuestre.

## Cómo verificar lo que hace la IA
- **Mutación manual:** rompé a propósito una línea (por ejemplo `is_allowed` devolviendo `True`). Si los tests siguen pasando, no sirven. Es lo primero que revisa el docente.
- **Leé los tests antes que el código.** Un test que no puede fallar no prueba nada.
- **Desconfiá de datos de seguridad "recordados"** (CVE, puntajes, flags de herramientas): verificalos contra la fuente o la versión instalada.
- **Pedí el diff, no el archivo completo,** y revisá qué tocó fuera del alcance de la tarea.

## Cuándo parar y preguntarle al docente
- El agente propone saltear un gate, ampliar el alcance del lab o agregar una verificación no inerte.
- Un test fallaba y el agente "lo arregló" cambiando el test.
- No entendés una decisión de diseño que el agente tomó y no podés justificarla.

## Errores frecuentes
| Error | Qué hacer |
|---|---|
| Pedir "implementá todo el sprint" | Dividir en un task por vez; commits pequeños |
| Dejar que el agente edite specs y código en el mismo paso | Primero spec y revisión, después código |
| Prompts de agentes de runtime con texto libre | Siempre con schema y validación; 2 fallos → HITL |
| Cambiar un prompt sin correr evals | Cada cambio de prompt o modelo = corrida de evals |
| Usar `shell=True` "para que ande" | Argv fijo; validar el target |

## Trabajo en equipo
- Una rama por change (`change/003-roe-and-tokens`), pull request con checklist: tests, evals, `progress.py`, revisión de otro integrante.
- El **Spec lead** aprueba los merges que cambian `openspec/`.
- Registrá en el informe técnico al menos **3 casos** en que la IA se equivocó y cómo lo detectaron.
