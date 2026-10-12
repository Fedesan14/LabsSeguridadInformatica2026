#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# start.sh — Lab Extra 2 (forense git). Sin Docker: genera el caso localmente.
set -euo pipefail
LABDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTF_ROOT="$(cd "$LABDIR/../.." && pwd)"; export CTF_ROOT
source "$CTF_ROOT/bin/lib/ui.sh"; source "$CTF_ROOT/bin/lib/banner.sh"
banner_lab "extra2" "EL REPO QUE DELATA — forense git"
if [ ! -d "$LABDIR/caso/repo-delata" ]; then
  ui_step "Generando el caso (repo con historia sospechosa)..."
  bash "$LABDIR/caso/generar-caso.sh"
  ui_ok "Caso listo."
else
  ui_info "El caso ya estaba generado. Para regenerarlo: rm -rf caso/repo-delata && bash caso/generar-caso.sh"
fi
echo
ui_info "Empezá la investigación:"
ui_dim  "   cd $LABDIR/caso/repo-delata"
ui_dim  "   git log --oneline --all"
echo
ui_info "Guía completa (leela antes de tocar nada):"
ui_dim  "   $LABDIR/README.md"
echo
ui_step "Entregar flag:   ./ctf submit extra2 R1 'FLAG{...}'"
ui_step "Ver progreso:    ./ctf status extra2"
