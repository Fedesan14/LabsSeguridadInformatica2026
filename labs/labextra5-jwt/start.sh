#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# start.sh — Lab Extra 5 (JWT). Sin Docker: Python puro.
set -euo pipefail
LABDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTF_ROOT="$(cd "$LABDIR/../.." && pwd)"; export CTF_ROOT
source "$CTF_ROOT/bin/lib/ui.sh"; source "$CTF_ROOT/bin/lib/banner.sh"
banner_lab "extra5" "JWT INSEGURO"
echo
ui_info "Sin Docker. Levantás el portal en una terminal y atacás desde otra."
echo
ui_step "1. Levantar el portal:   python3 $LABDIR/objetivo/server.py"
ui_step "2. Conseguir un token:   curl 'localhost:8080/login?user=diego&pass=diego123'"
ui_step "3. Tu navaja (TODOs):    $LABDIR/src/jwt_tool.py"
ui_dim  "   python3 src/jwt_tool.py decodificar <token>"
ui_dim  "   python3 src/jwt_tool.py crackear <token> caso/diccionario.txt"
ui_dim  "   python3 src/jwt_tool.py forjar <secreto> --sub diego --role admin"
echo
ui_info "Guía completa (leela antes de tocar nada):"
ui_dim  "   $LABDIR/README.md"
echo
ui_step "Entregar flag:   ./ctf submit extra5 R1 'FLAG{...}'"
ui_step "Ver progreso:    ./ctf status extra5"
