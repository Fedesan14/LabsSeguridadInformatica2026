# Research — Lab Extra SSRF

> Copiá a `entregas/labextra/grupoXX/research.md`. Extensión: 1 a 2 carillas.
> Citá las fuentes (links). Declaración de IA obligatoria como en el informe.

## Opción A — Un caso real

Elegí un incidente o writeup real de SSRF (Capital One 2019, o un reporte
público de bug bounty) y contalo en formato de lección:

1. ¿Qué funcionalidad era vulnerable?
2. ¿Qué pidió el atacante a través del servidor?
3. ¿Qué obtuvo y cuál fue el impacto?
4. ¿Qué mitigación lo habría impedido?

## Opción B — El metadata service

Investigá el metadata service de una nube (AWS `169.254.169.254`, GCP
`metadata.google.internal`, Azure `169.254.169.254`):

1. ¿Qué información expone y a quién?
2. ¿Por qué un SSRF lo convierte en robo de credenciales?
3. ¿Qué es IMDSv2 (AWS) y qué ataque bloquea?
4. ¿Cómo se relaciona con lo que hiciste en R1 de este lab?

## Pregunta de cierre (obligatoria en ambas opciones)

¿Qué similitud y qué diferencia hay entre "el server fetchea por vos" (SSRF) y
"el server ejecuta por vos" (inyección de comandos, Lab 07)? ¿Cuál te parece
más peligrosa y por qué?
