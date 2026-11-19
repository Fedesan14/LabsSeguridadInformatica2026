# Rúbrica — Lab Extra 5: JWT inseguro (sobre 100 puntos)

| Criterio | Puntos |
|---|---|
| **jwt_tool.py funcional.** Las 4 funciones implementadas; `forjar` produce tokens que el servidor acepta. | 25 |
| **Cadena de los 3 retos documentada.** Comandos + salidas + razonamiento. | 20 |
| **P1–P2 (integridad vs confidencialidad; crack offline).** Los dos conceptos centrales del lab. | 20 |
| **P3–P4 (IDOR en el claim; alg:none).** | 15 |
| **P5 (defensas priorizadas).** RS256/EdDSA vs secreto fuerte: entienden la diferencia estructural. | 15 |
| **Evidencia y protocolo.** Ver `docs/PROTOCOLO-EVIDENCIA.md`. | 5 |

## Reglas

- **El control de sanidad es obligatorio** (§4 del entregable): un lab de
  firma digital sin demostrar el rechazo de tokens inválidos es un lab a medias.
- Usar `pyjwt` o jwt.io para el crack: válido para *verificar*, pero el
  cracker y la forja tienen que estar en tu `jwt_tool.py` (stdlib).
- Defensa oral a sorteo: un integrante explica por qué HMAC permite crack
  offline y RS256 no (clave pública verifica, clave privada firma).
- Declaración de IA obligatoria.
