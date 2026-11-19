# Cómo publicar el kit en un repositorio y que los equipos lo continúen

## Resumen
Se crea **un repositorio plantilla** con el contenido del zip; cada equipo lo copia con "Use this template" y trabaja en su propio repositorio con CI, protección de rama e issues generados desde los `tasks.md`. Los pasos con GitHub se probaron solo en parte (ver "Qué se verificó"); el resto sigue la documentación habitual de GitHub y conviene confirmarlo la primera vez.

## Requisitos
- Cuenta de GitHub (organización de la cátedra o cuenta del docente) y `git` instalado.
- Opcional: GitHub CLI (`gh`) autenticado con `gh auth login`.
- Python 3.12 para verificar localmente.

## Paso 1 · Descomprimir y verificar localmente
```bash
unzip ptaas-kit.zip && cd ptaas-kit
python -m venv .venv && source .venv/bin/activate     # en Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q
python evals/run_evals.py --mode golden
python tools/progress.py
```
Los tres comandos deben terminar en verde antes de publicar.

## Paso 2 · Crear el repositorio vacío
En GitHub, **New repository**: nombre sugerido `ptaas-plantilla`, **privado**, y **sin** README, `.gitignore` ni licencia (ya vienen en el kit).

## Paso 3 · Subir el contenido
Opción A, con `git`:
```bash
git init -b main          # si tu git es antiguo: git init && git branch -M main
git add .
git status                # revisá que no haya .env, claves ni archivos .db
git commit -m "Kit inicial PTaaS"
git remote add origin https://github.com/<organización>/ptaas-plantilla.git
git push -u origin main
```
Opción B, con `gh` (crea el repositorio y sube en un paso):
```bash
git init -b main && git add . && git commit -m "Kit inicial PTaaS"
gh repo create <organización>/ptaas-plantilla --private --source=. --remote=origin --push
```

## Paso 4 · Convertirlo en plantilla
En el repositorio: **Settings → General → Template repository** (activar). Cada equipo hará **Use this template → Create a new repository** y obtendrá su copia con el historial limpio.

## Paso 5 · Configurar cada repositorio de equipo
1. **Actions:** en la pestaña *Actions* verificá que el workflow `ci` corra en el primer push. Debe terminar en verde.
2. **Protección de `main`** (Settings → Branches → Add rule): exigir pull request, 1 aprobación como mínimo, que el check `verificar` pase y bloquear force-push.
3. **Colaboradores:** invitar a los integrantes con rol *Write*; el docente como *Admin* o *Maintain*.
4. **Seguridad:** activar *Secret scanning* y *Push protection* si el plan lo permite.
5. **Issues y sprints:** crear los milestones `Sprint 1`, `Sprint 2` y `Sprint 3` y la etiqueta `task`.
6. **Tablero** (pestaña *Projects*): columnas Backlog, En curso, En revisión y Hecho.

## Paso 6 · Generar los issues desde los tasks
```bash
python tools/create_issues.py                 # muestra qué crearía (no ejecuta nada)
python tools/create_issues.py --apply --repo <organización>/<repositorio>   # los crea con gh
```
Genera un issue por cada `- [ ]` pendiente de los changes 002 a 007, con la plantilla de task y el milestone del sprint correspondiente.

## Paso 7 · Cómo trabaja cada equipo
1. Leer `README.md`, `CONTRIBUTING.md`, `docs/marco-teorico.md` y `docs/plan-15-dias.md`.
2. Tomar un issue, crear la rama `change/<id>` y seguir el orden: spec, revisión, test, código, revisión de seguridad.
3. Abrir un pull request con la plantilla; otra persona lo revisa; el CI tiene que estar en verde.
4. Al terminar un change, archivar su delta en `openspec/specs/`.
5. Actualizar `python tools/progress.py` antes de cada checkpoint con el docente.

## Qué NO se sube nunca
Claves de API (por ejemplo la de `evals/run_evals.py --mode live`), archivos `.env`, bases de datos de bitácora de ejecuciones reales, ni nada que no sea del laboratorio propio. Si algo se filtra: rotarlo de inmediato, porque borrar el commit no revierte la exposición.

## Licencia
El kit **no incluye licencia** a propósito: elegirla es una decisión de la cátedra o de la institución. Hasta que se agregue una, el material queda con todos los derechos reservados. Si se publica en abierto, agregá un archivo `LICENSE` antes de abrir el repositorio.

## Qué se verificó y qué no
- **Verificado en este entorno:** instalación en un entorno limpio, 77 tests, evals golden, `tools/progress.py` y la validez del YAML del workflow.
- **No verificado:** la ejecución real del workflow en GitHub, `gh repo create` y las reglas de protección, porque no hay acceso a GitHub desde acá. Probalos primero con el repositorio plantilla.
- **Tampoco probado:** `lab/docker-compose.yml` y las evals con modelos reales (`--mode live`).

## Problemas frecuentes
| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El CI falla en `tools/progress.py` | Una spec declara un archivo de test que no existe | Corregir la línea `Tests:` de esa spec |
| `git push` rechazado | El repositorio remoto se creó con README o licencia | Crear uno vacío o hacer `git pull --rebase origin main` |
| El check `verificar` no aparece en la regla de rama | El workflow todavía no corrió | Hacer un push y volver a configurar la regla |
| Los tests fallan solo en tu máquina | Versión de Python distinta | Usar 3.12, como el CI |
