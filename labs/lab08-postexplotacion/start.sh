#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# start.sh — genérico. Arranca el lab: banner, levanta el entorno y abre la guía.
# No hace falta editarlo: deriva el número y el tema del nombre del directorio.
set -euo pipefail
LABDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTF_ROOT="$(cd "$LABDIR/../.." && pwd)"; export CTF_ROOT
source "$CTF_ROOT/bin/lib/ui.sh"; source "$CTF_ROOT/bin/lib/banner.sh"
NAME="$(basename "$LABDIR")"                       # labNN-tema-largo
NUM="$(echo "$NAME" | sed 's/^lab//; s/-.*//')"
TEMA="$(echo "$NAME" | sed 's/^lab[0-9]*-//; s/-/ /g' | tr '[:lower:]' '[:upper:]')"
banner_lab "$NUM" "$TEMA"
if [ -f "$LABDIR/entorno/target.compose.yml" ]; then
  ui_step "Levantando el entorno Docker (consola atacante + target)..."
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    ( cd "$CTF_ROOT" && make -s lab N="$NUM" ) && ui_ok "Entorno arriba."
    echo; ui_info "Entrá a la consola y empezá:"; ui_dim "   make shell"
  else
    ui_warn "Docker no está corriendo. Arrancá Docker Desktop y reintentá."
  fi
else
  ui_info "Este lab no usa Docker (es de teoría/código)."
fi
echo
ui_info "Guía completa (leela toda antes de tirar comandos):"
ui_dim  "   $LABDIR/README.md"
if [ -f "$LABDIR/retos.manifest" ]; then
  echo; ui_step "Entregar flag:   ./ctf submit $NUM R1 'FLAG{...}'"
  ui_step "Ver progreso:    ./ctf status $NUM"
fi
