# Prompts de agentes de runtime

- `01` Scope Guard y `07` Reviewer **no tienen prompt**: el Guard es código determinista (`harness/contracts.py`) y el Reviewer es humano.
- Los demás agentes se cargan según `harness/models.yaml`.
- Todo cambio de prompt = delta de spec + corrida de evals sobre el laboratorio.
