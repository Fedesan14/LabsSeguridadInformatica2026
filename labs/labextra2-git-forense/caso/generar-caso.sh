#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# generar-caso.sh — construye el "repo que delata": un repositorio git con una
# historia realista donde PhantomCorp filtró secretos y creyó borrarlos.
#
# Uso:  bash caso/generar-caso.sh
# Crea: caso/repo-delata/  (un repo git común y corriente — clonealo o entrá)
#
# El script es DETERMINISTA (fechas y autores fijos): todos los grupos
# investigan exactamente la misma evidencia.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$DIR/repo-delata"

rm -rf "$REPO"
mkdir -p "$REPO"
cd "$REPO"
git init -q -b main
git config user.name "dev-jperez"
git config user.email "jperez@phantomcorp.example"

# Fechas fijas => historia idéntica para todos los grupos.
export GIT_AUTHOR_DATE="2026-08-10T09:12:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"

# --- commit 1: nace el proyecto ---------------------------------------------
cat > app.py <<'EOF'
#!/usr/bin/env python3
"""deploy-tool — automatiza el deploy de la intranet PhantomCorp."""
import os

API_URL = "https://api.phantomcorp.example/v2"

def deploy(entorno: str) -> None:
    token = os.environ.get("PHANTOM_API_TOKEN")
    if not token:
        raise SystemExit("Falta PHANTOM_API_TOKEN en el entorno")
    print(f"deploy a {entorno} contra {API_URL} (token ***)")

if __name__ == "__main__":
    deploy("staging")
EOF
cat > README.md <<'EOF'
# deploy-tool

Herramienta interna de deploys. El token va por variable de entorno.
EOF
git add -A
git commit -q -m "inicial: deploy-tool con token por variable de entorno"

# --- commit 2: EL ERROR — la key entra a la historia ------------------------
export GIT_AUTHOR_DATE="2026-08-10T18:47:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
cat > config.py <<'EOF'
# Config de emergencia — arreglar el deploy roto YA (después lo pasamos a env)
PHANTOM_API_TOKEN = "FLAG{git_log_no_olvida}"
REGION = "us-east-1"
DEBUG = True
EOF
git add config.py
git commit -q -m "hotfix: deploy roto en produccion (config temporal)"

# --- commit 3: la "limpieza" que no limpia ----------------------------------
export GIT_AUTHOR_DATE="2026-08-11T10:05:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
cat > config.py <<'EOF'
# Config — sin secretos, por fin
REGION = "us-east-1"
DEBUG = False
EOF
git add config.py
git commit -q -m "fix: sacar credenciales del codigo (ups)"

# --- commit 4: trabajo que quedó "perdido" por un reset ---------------------
export GIT_AUTHOR_DATE="2026-08-12T14:22:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
cat > notas_investigacion.txt <<'EOF'
NOTAS — pruebas de acceso al cluster nuevo (NO SUBIR)
====================================================
El equipo de infra me paso la llave del cluster de staging para probar:

    staging_key: FLAG{git_reflog_rescata}

Cuando este todo migrado esto se rota y estas notas se borran.
EOF
git add notas_investigacion.txt
git commit -q -m "wip: notas del cluster nuevo (no mergear todavia)"
# El dev "se arrepiente" y resetea: el commit queda colgado (dangling),
# recuperable por reflog/fsck. En GitHub habría quedado en la API igual.
git reset -q --hard HEAD~1

# --- rama abandonada con un .env --------------------------------------------
export GIT_AUTHOR_DATE="2026-08-05T16:30:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
git checkout -q -b feature/pasarela-pagos HEAD~1
cat > .env.pasarela <<'EOF'
# NO COMMITEAR ESTO (lo commitee igual, despues lo veo)
PAGOS_SECRET=FLAG{git_rama_abandonada}
PAGOS_ENDPOINT=https://pagos.phantomcorp.example
EOF
cat > pasarela.py <<'EOF'
"""Integracion con la pasarela de pagos (WIP, quedo a mitad de camino)."""
EOF
git add -A
git commit -q -m "wip: pasarela de pagos (falta todo)"
git checkout -q main

# --- commit final: el repo queda "lindo" para entregar ----------------------
export GIT_AUTHOR_DATE="2026-08-20T11:00:00 -03:00"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
cat >> README.md <<'EOF'

## Estado

Listo para produccion. Historia limpia. Sin secretos. ✅
EOF
git add README.md
git commit -q -m "docs: estado del proyecto"

echo
echo "Caso generado en:  $REPO"
echo "Es un repo git común. Entrá y foreseá:"
echo "   cd $REPO"
echo "   git log --oneline"
