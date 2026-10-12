#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# setup.sh — prepara el host comprometido (corre como root en el build).
set -e
d() { echo "$1" | base64 -d; }   # des-ofusca una flag

# R1 — enumeracion del filesystem: nota de deploy legible por operador
mkdir -p /opt/phantom-deploy
{ echo "PhantomCorp - notas de despliegue (NO borrar)"; \
  echo "deploy_token=$(d 'RkxBR3twb3N0X3NpdHVhdGlvbmFsX2F3YXJlbmVzc30=')"; } > /opt/phantom-deploy/DEPLOY_NOTES.txt
chmod 644 /opt/phantom-deploy/DEPLOY_NOTES.txt

# R2 — loot: credenciales en el .env de la app (legible) + bash_history
mkdir -p /var/www
cat > /var/www/.env <<E
DB_HOST=phantomcorp-db
DB_USER=phantom_app
DB_PASS=Ph@ntom-DB-2024
APP_SECRET=$(d 'RkxBR3tsb290X2NyZWRlbnRpYWxzX2ZvdW5kfQ==')
E
chmod 644 /var/www/.env
cat > /home/operador/.bash_history <<E
ls -la
cat /var/www/.env
curl http://phantomcorp-db/
E
chown operador:operador /home/operador/.bash_history

# R3 — privilege escalation: binario SUID (copia de bash) + flag solo-root
cp /bin/bash /usr/local/bin/system-check
chmod 4755 /usr/local/bin/system-check
d 'RkxBR3twcml2ZXNjX3N1aWRfcm9vdH0=' > /root/flag.txt
chmod 600 /root/flag.txt
chown root:root /root/flag.txt
