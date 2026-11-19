# Ruteo de modelos y "tuning" por agente

## Resumen
- **Opus 5.5** donde hay planificación o riesgo (Orchestrator, Validation).
- **Sonnet 5.5** para el trabajo de volumen medio (Recon, Correlación, Análisis, Reporting).
- **Haiku 5.5** para triage/parsing masivo.
- **Código determinista** para el Scope Guard; **humano** para el Reviewer.

## Parámetros
| Agente | Modelo | Temp | Por qué |
|---|---|---|---|
| Orchestrator | opus-5-5 | 0.2 | Planifica; un mal plan propaga errores |
| Scope Guard | — (código) | — | Autorización = garantía, no probabilidad |
| Asset Discovery | sonnet-5-5 | 0.1 | Decisiones acotadas sobre salida de tools |
| Correlation | sonnet-5-5 | 0.0 | Mapeo estructurado, reproducible |
| Vuln Analysis | sonnet-5-5 | 0.1 | Hipótesis/refinamiento (loop B) |
| Validation | opus-5-5 | 0.0 | Selección/parametrización precisa del PoC |
| Reporting | sonnet-5-5 | 0.3 | Prosa clara, algo de variación |
| Triage/Parser | haiku-5-5 | 0.0 | Volumen, costo bajo |

## Reglas transversales de prompting
1. **Rol + mandato + prohibiciones explícitas** al inicio (ver `prompts/`).
2. **Salida con schema** (Pydantic/JSON); sin texto libre en canales entre agentes.
3. **Contexto mínimo** (menor privilegio): cada agente ve solo su fase.
4. **Condición de parada** y tope de iteraciones en todo loop.
5. **Evals por agente**: dataset sobre el laboratorio (DVWA/Juice Shop) con salidas esperadas; correr en CI antes de cambiar modelo o prompt.
6. Cambio de modelo/prompt = delta de spec + corrida de evals (trazabilidad ISO/IEC 27001 / tablero SDLC).

## Fallback
Si el schema falla 2 veces → escalar a HITL; no reintentar indefinidamente. Si un modelo no está disponible → fallback al mismo tier inferior solo para agentes de bajo riesgo (Recon/Reporting); nunca para Orchestrator ni Validation (pausar y notificar).
