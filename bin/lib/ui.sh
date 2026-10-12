#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# ui.sh — helpers de presentación (colores, cajas, barras). Sin dependencias.
# El color se activa solo si la salida es una terminal (respeta pipes y CI).
if [ -t 1 ] && [ "${NO_COLOR:-}" = "" ]; then
  C_RESET=$'\033[0m'; C_DIM=$'\033[2m'; C_BOLD=$'\033[1m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
  C_BLUE=$'\033[34m'; C_MAGENTA=$'\033[35m'; C_CYAN=$'\033[36m'; C_GREY=$'\033[90m'
else
  C_RESET=""; C_DIM=""; C_BOLD=""; C_RED=""; C_GREEN=""; C_YELLOW=""
  C_BLUE=""; C_MAGENTA=""; C_CYAN=""; C_GREY=""
fi
ui_ok()   { printf '%s[ OK ]%s %s\n' "$C_GREEN"  "$C_RESET" "$*"; }
ui_fail() { printf '%s[FAIL]%s %s\n' "$C_RED"    "$C_RESET" "$*"; }
ui_warn() { printf '%s[ !! ]%s %s\n' "$C_YELLOW" "$C_RESET" "$*"; }
ui_info() { printf '%s[ .. ]%s %s\n' "$C_CYAN"   "$C_RESET" "$*"; }
ui_step() { printf '%s>>%s %s\n'     "$C_MAGENTA" "$C_RESET" "$*"; }
ui_dim()  { printf '%s%s%s\n'        "$C_GREY"   "$*" "$C_RESET"; }
ui_box() {
  local text="$1" width=60 pad
  printf '%s' "$C_CYAN"
  printf '  ╭'; printf '─%.0s' $(seq 1 $width); printf '╮\n'
  pad=$(( (width - ${#text}) / 2 ))
  printf '  │%*s%s%*s│\n' "$pad" "" "$text" "$(( width - pad - ${#text} ))" ""
  printf '  ╰'; printf '─%.0s' $(seq 1 $width); printf '╯'
  printf '%s\n' "$C_RESET"
}
ui_bar() {
  local done=$1 total=$2 width=30 filled empty pct
  [ "$total" -eq 0 ] && total=1
  filled=$(( done * width / total )); empty=$(( width - filled )); pct=$(( done * 100 / total ))
  printf '  %s' "$C_GREEN"; [ "$filled" -gt 0 ] && printf '█%.0s' $(seq 1 "$filled")
  printf '%s' "$C_GREY";  [ "$empty" -gt 0 ] && printf '░%.0s' $(seq 1 "$empty")
  printf '%s  %d/%d (%d%%)\n' "$C_RESET" "$done" "$total" "$pct"
}
