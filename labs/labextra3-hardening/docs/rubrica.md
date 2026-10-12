# Rúbrica — Lab Extra 3: Defendé PhantomCorp (sobre 100 puntos)

| Criterio | Puntos |
|---|---|
| **Las 5 defensas funcionan.** Verificador en 5/5 contra la copia del grupo. | 25 |
| **Calidad de los parches.** El diff muestra fixes estructurales (parametrización, confinamiento de path), no parches cosméticos (filtros de strings, "sacar del robots"). | 25 |
| **Sin regresión funcional.** La app sigue operando: `/`, login legítimo, descarga legítima. | 15 |
| **P1–P2 (evidencia antes/después + defensa real vs ilusoria).** | 15 |
| **P3–P5 (seguridad por oscuridad, por qué parametrizar, ranking de gravedad).** | 15 |
| **Evidencia y protocolo.** comandos.txt + salidas crudas + declaración de IA (ver `docs/PROTOCOLO-EVIDENCIA.md`). | 5 |

## Reglas

- **El verificador miente si lo engañás a propósito**: hardcodear respuestas
  para que el chequeo dé verde sin arreglar el problema (ej. devolver 404 solo
  cuando el path contiene "etc/passwd") es fraude académico, no ingenio. Se
  detecta en la revisión del diff y en la defensa oral.
- **Defensa oral a sorteo**: el docente elige UNA defensa y un integrante la
  explica línea por línea en vivo, y puede pedir una variante del ataque
  (ej. `%2e%2e%2f` para D5) para ver si el fix resiste.
- Informe sin evidencia = devolución. Declaración de IA obligatoria.
