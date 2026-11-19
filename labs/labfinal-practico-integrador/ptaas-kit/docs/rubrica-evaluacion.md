# Rúbrica de evaluación (propuesta, ajustable)

## Resumen
Se evalúa tanto **el control** (que el sistema impida lo no autorizado) como **la inteligencia** (que los agentes aporten). Seis criterios, 100 puntos, 4 niveles. Cada criterio exige **evidencia verificable** en el repositorio: nada se puntúa solo por declaración.

| Criterio | Peso |
|---|---|
| 1. Harness e invariantes | 25 |
| 2. Diseño del swarm y los loops | 20 |
| 3. Specs y tests | 15 |
| 4. Herramientas y adaptadores | 15 |
| 5. Informe, evals y demo | 15 |
| 6. Ética, gobernanza y trabajo con IA | 10 |

## Niveles por criterio

### 1. Harness e invariantes (25)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial (0–9) | Hay guard pero se puede evitar o no registra bloqueos | Tests que fallan al intentar un bypass |
| En desarrollo (10–16) | Invariantes I1–I8 en su mayoría, con huecos | Matriz invariante → test incompleta |
| Logrado (17–22) | Todos los invariantes con tests; bitácora persistente verificable | `audit verify` detecta alteración y borrado |
| Sobresaliente (23–25) | Además, red team propio documentado con bypass hallados y corregidos | ≥ 10 tests adversariales con historia en commits |

### 2. Diseño del swarm y los loops (20)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial | Agentes sin mandato claro o con salida en texto libre | Prompts sin schema |
| En desarrollo | Mandatos y schemas definidos; un loop sin tope claro | Un loop corriendo |
| Logrado | Los 3 loops con parada, tope y no-progreso; escalado a HITL | Tests de `decide_*` + corrida contra el lab |
| Sobresaliente | Además, justificación del ruteo de modelos con datos de evals | Comparativa de modelos por agente |

### 3. Specs y tests (15)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial | Código sin spec o specs sin Scenarios negativos | — |
| En desarrollo | Specs actualizadas; cobertura parcial de Scenarios | `progress.py` < 100 % |
| Logrado | Cada Scenario tiene test; deltas archivados | `progress.py` 100 % |
| Sobresaliente | Mutation checks que demuestran que los tests detectan roturas | Informe de mutaciones y correcciones |

### 4. Herramientas y adaptadores (15)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial | Uso directo de binarios fuera de adaptadores | — |
| En desarrollo | Adaptadores con fixtures, sin corrida real | Tests con salidas grabadas |
| Logrado | Corridas reales contra el lab; templates curados y registrados | `MANIFEST.md` y bitácora |
| Sobresaliente | Un adaptador nuevo propio, con revisión y tests de bloqueo | Change archivado |

### 5. Informe, evals y demo (15)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial | Informe sin CWE/CVSS o demo no repetible | — |
| En desarrollo | Informe completo; demo con pasos manuales | — |
| Logrado | Un comando ejecuta el recorrido; evals ≥ 20 casos con análisis | Informe de evals |
| Sobresaliente | Evals en vivo comparando versiones de prompts, con mejoras medidas | Tabla antes/después |

### 6. Ética, gobernanza y trabajo con IA (10)
| Nivel | Descripción | Evidencia |
|---|---|---|
| Inicial | Se saltean gates o se ejecuta fuera del lab | **Nota máxima del trabajo: 4/10 en este criterio y revisión docente** |
| En desarrollo | Reglas cumplidas, sin reflexión | — |
| Logrado | Retrospectiva con ejemplos de errores de la IA detectados y corregidos | Informe técnico |
| Sobresaliente | Propuesta de controles adicionales justificados con estándares (ISO/IEC 29147, 30111, NIST 800-115) | Change propuesto |

## Descalificantes
Se anula el trabajo si hay **acciones contra sistemas que no sean el laboratorio propio**, evasión deliberada de gates, o ampliación del catálogo con verificaciones no inertes sin aprobación.

## Cómo se puntúan los checkpoints
Cada checkpoint vale como entrega parcial (no suma puntos extra, pero un checkpoint sin evidencia limita el nivel máximo del criterio relacionado a "En desarrollo").
