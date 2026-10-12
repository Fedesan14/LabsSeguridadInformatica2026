#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# start.sh — Lab Extra 3 (hardening). Sin Docker: Python puro.
set -euo pipefail
LABDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTF_ROOT="$(cd "$LABDIR/../.." && pwd)"; export CTF_ROOT
source "$CTF_ROOT/bin/lib/ui.sh"; source "$CTF_ROOT/bin/lib/banner.sh"
banner_lab "extra3" "DEFENDÉ PHANTOMCORP — hardening"
echo
ui_info "Este lab es DEFENSIVO y no usa Docker: parchás una app vulnerable en Python."
echo
ui_step "1. Mirá el verificador atacar el objetivo roto:"
ui_dim  "   python3 $LABDIR/verificar-defensa.py"
ui_step "2. Copiá el objetivo a TU entrega y parchalo ahí:"
ui_dim  "   cp -r $LABDIR/objetivo $CTF_ROOT/entregas/labextra3/grupoXX/objetivo"
ui_step "3. Verificá tu parche (te da las flags por cada defensa):"
ui_dim  "   python3 $LABDIR/verificar-defensa.py --dir $CTF_ROOT/entregas/labextra3/grupoXX/objetivo"
echo
ui_info "Guía completa (leela antes de tocar nada):"
ui_dim  "   $LABDIR/README.md"
echo
ui_step "Entregar flag:   ./ctf submit extra3 D1 'FLAG{...}'"
ui_step "Ver progreso:    ./ctf status extra3"
