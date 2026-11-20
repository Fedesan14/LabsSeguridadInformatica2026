#!/usr/bin/env bash
# Arranque del swarm PTaaS en un solo comando: construye el sandbox, levanta el
# blanco (phantomcorp) y abre el panel web. Se puede correr desde cualquier lado:
# el script se ubica solo en la raíz del repo.
#   Arrancar:  ./entregas/labfinal/grupo03/ptaas/levantar.sh
#   Bajar:     ./entregas/labfinal/grupo03/ptaas/levantar.sh down
set -e

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
compose="docker compose -p cyberlab --project-directory . \
  -f entorno/docker-compose.yml \
  -f labs/labfinal-practico-integrador/entorno/target.compose.yml"
py="$(command -v python3 || command -v python)"

if [ "$1" = "down" ]; then
  $compose down
  exit 0
fi

echo "[1/3] Chequeando Docker..."
docker info >/dev/null 2>&1 || { echo "Docker no responde. Abrí Docker Desktop y esperá a 'Engine running'."; exit 1; }

echo "[2/3] Construyendo la imagen del sandbox (ptaas-runner)..."
docker build -t ptaas-runner -f entregas/labfinal/grupo03/ptaas/Dockerfile.runner entregas/labfinal/grupo03/ptaas

echo "[3/3] Levantando el blanco (phantomcorp)..."
$compose up -d --build phantomcorp

echo
echo "Listo. Abriendo el panel en http://127.0.0.1:8765/  (Ctrl+C para cerrarlo)."
echo "Para bajar el lab al terminar:  ./entregas/labfinal/grupo03/ptaas/levantar.sh down"
echo
exec "$py" entregas/labfinal/grupo03/ptaas/panel.py
