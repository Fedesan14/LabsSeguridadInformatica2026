# Protocolo de evidencia — cómo se reportan los trabajos

> Documento para alumnos y docentes. Define **qué se adjunta además del
> informe** en cualquier práctico del curso, y por qué.

## La idea

Una flag o una respuesta se pueden copiar. Una **cadena de trabajo** no. Por
eso cada entrega tiene tres capas:

1. **El informe** — lo que entendiste (rúbrica).
2. **La evidencia** — lo que hiciste (comandos, salidas, capturas).
3. **El historial del PR** — quién hizo qué (commits de todos los integrantes).

## Qué se adjunta en TODA entrega

| Pieza | Dónde | Qué demuestra |
|---|---|---|
| `informe.md` | `entregas/labNN/grupoXX/` | Razonamiento y análisis |
| `evidencia/comandos.txt` | mismo | Los comandos usados, en orden (salida de `history` o listado fiel) |
| `evidencia/salidas/` | mismo | Salidas crudas redirigidas con `>` de los comandos clave |
| Captura de `./ctf status` | en el informe | Progreso de flags |
| Declaración de IA | en el informe | Transparencia obligatoria |
| Commits del PR | GitHub | Contribución de todos los integrantes |

Reglas de la evidencia:

- **Cruda, no editada.** Las salidas se guardan con redirección
  (`comando > salidas/r1.txt`), no copiadas a mano. El docente puede comparar
  contra el entorno.
- **Coherente con el informe.** Si el informe dice "usamos nmap -p-", la
  evidencia tiene que mostrar ese nmap. Inconsistencia = se revisa todo.
- **Sin secretos reales.** Jamás subir API keys propias, tokens del LLM del
  Lab 09, ni datos personales. La evidencia es contra los labs, no contra
  terceros.

## Defensa oral (a sorteo)

Cualquier entrega puede cerrar con **5 minutos de defensa**: el docente elige
un integrante y un hallazgo, y el integrante lo **reproduce en vivo**
(regenerar el entorno y llegar a la flag). No es un examen extra: es la
verificación de que el trabajo es del grupo.

## Para el docente: cómo pedirlo en una consigna

Texto listo para pegar en el anuncio de cualquier lab:

> Además del informe, adjunten en `entregas/labNN/grupoXX/`:
> (1) `evidencia/comandos.txt` con todos los comandos usados, en orden;
> (2) `evidencia/salidas/` con las salidas crudas de los comandos que
> encontraron cada flag (redirigidas con `>`, sin editar);
> (3) captura de `./ctf status NN` completa;
> (4) declaración de IA.
> Puede haber defensa oral de 5 minutos a sorteo: cualquier integrante tiene
> que poder reproducir cualquier hallazgo en vivo. Ver
> `docs/PROTOCOLO-EVIDENCIA.md`.

## Verificación rápida (docente)

```bash
# ¿la evidencia existe y no está vacía?
ls -la entregas/labNN/grupoXX/evidencia/
# ¿los commits del PR son de todos?
gh pr view <N> --json commits --jq '.commits[].authors[].login' | sort -u
```
