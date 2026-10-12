# Rúbrica — Lab Extra 4: Cracking de contraseñas (sobre 100 puntos)

| Criterio | Puntos |
|---|---|
| **cracker.py funcional.** Diccionario + reglas + descifrado de loot. Código propio, stdlib. | 25 |
| **Resultados (R1–R3).** Las 3 cuentas crackeadas con loot abierto y flags entregadas. | 20 |
| **P1 (medición).** Intentos/segundo medidos (no inventados) y extrapolación a GPU correcta en orden de magnitud. | 15 |
| **P2 (salt) y P4 (trabajo por intento).** Las dos preguntas conceptuales centrales del lab. | 20 |
| **P3 (políticas) y P5 (respuesta).** NIST 800-63B correctamente aplicado; respuesta de incidente ordenada. | 15 |
| **Evidencia y protocolo.** Ver `docs/PROTOCOLO-EVIDENCIA.md`. | 5 |

## Reglas

- La contraseña de `root` **no existe en el caso**: es imposible por diseño.
  Cualquier grupo que "la haya crackeado" la sacó de otro lado — eso es fraude,
  no mérito. El análisis correcto es explicar *por qué no cae*.
- Usar `john`/`hashcat` reales en vez del cracker propio: no suma para la nota
  (el lab es implementar, no instalar), pero como comparación de velocidad en
  P1 es bienvenido y puntúa.
- Defensa oral a sorteo: un integrante explica `aplicar_reglas()` y por qué
  `phantom` estaba en el diccionario pero `phantom2026` no.
- Declaración de IA obligatoria.
