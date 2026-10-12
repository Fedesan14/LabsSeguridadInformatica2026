# Research — Lab Extra 2: El repo que delata

> Copiá a `entregas/labextra2/grupoXX/research.md`. Extensión: 1 a 2 carillas.
> Citá las fuentes. Declaración de IA obligatoria.

## Opción A — Herramientas reales

Compará dos herramientas del ecosistema de secretos en git:

- **Detección:** Gitleaks, TruffleHog, GitHub Secret Scanning, GitGuardian.
- **Limpieza:** `git filter-repo`, BFG Repo-Cleaner.

Para cada una: qué busca, cómo la usarías en un pipeline de CI, y qué **no**
resuelve.

## Opción B — Un incidente real

Buscá un caso documentado de compromiso por credenciales filtradas en un
repositorio (post-mortems, reportes de bug bounty, notas técnicas). Contalo en
formato lección: qué se filtró, cuánto tiempo estuvo expuesto, cómo lo
encontraron, qué habría cambiado con rotación inmediata.

## Pregunta de cierre (obligatoria en ambas opciones)

GitHub escanea pushes públicos buscando secretos y avisa a los proveedores
(AWS, etc.) para revocarlos. ¿Por qué eso **no** te salva igual? Mencioná al
menos dos ventanas de exposición que quedan abiertas.
