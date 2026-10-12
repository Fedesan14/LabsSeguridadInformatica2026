#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# start.sh — Lab Extra 4 (cracking). Sin Docker: Python puro.
set -euo pipefail
LABDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTF_ROOT="$(cd "$LABDIR/../.." && pwd)"; export CTF_ROOT
source "$CTF_ROOT/bin/lib/ui.sh"; source "$CTF_ROOT/bin/lib/banner.sh"
banner_lab "extra4" "CRACKING DE CONTRASEÑAS"
echo
ui_info "Sin Docker. Completás src/cracker.py (stdlib) y crackeás caso/sombra.txt."
echo
ui_step "Empezar:"
ui_dim  "   cd $LABDIR"
ui_dim  "   python3 src/cracker.py crackear caso/sombra.txt caso/diccionario.txt"
ui_step "Abrir un loot con la contraseña crackeada:"
ui_dim  "   python3 src/cracker.py descifrar caso/loot/operador.enc --password <...>"
echo
ui_info "Guía completa (leela antes de tocar nada):"
ui_dim  "   $LABDIR/README.md"
echo
ui_step "Entregar flag:   ./ctf submit extra4 R1 'FLAG{...}'"
ui_step "Ver progreso:    ./ctf status extra4"
