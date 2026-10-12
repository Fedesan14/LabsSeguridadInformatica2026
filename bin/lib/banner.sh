#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# banner.sh — arte ASCII del curso.
banner_main() {
  printf '%s' "${C_CYAN}${C_BOLD}"
  cat <<'ART'

   ██████╗██╗   ██╗██████╗ ███████╗██████╗     ██╗      █████╗ ██████╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██║     ██╔══██╗██╔══██╗
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██║     ███████║██████╔╝
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║     ██╔══██║██╔══██╗
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ███████╗██║  ██║██████╔╝
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═════╝
ART
  printf '%s' "${C_RESET}"
  printf '  %sSeguridad Informática · UTN FRVM · 2026%s\n' "$C_DIM" "$C_RESET"
  printf '  %sde la tríada CIA a los agentes ofensivos autónomos%s\n\n' "$C_GREY" "$C_RESET"
}
banner_lab() {   # banner_lab "05" "RECONOCIMIENTO"
  printf '%s' "${C_MAGENTA}${C_BOLD}"
  cat <<ART

  ┌──────────────────────────────────────────────────────┐
  │  LABORATORIO $1  ·  $2
  └──────────────────────────────────────────────────────┘
ART
  printf '%s\n' "${C_RESET}"
}
banner_victory() {
  printf '%s' "${C_GREEN}${C_BOLD}"
  cat <<'ART'
       ★  ★  ★   FLAG CAPTURADA   ★  ★  ★
            \(^o^)/   +1 al score
ART
  printf '%s\n' "${C_RESET}"
}
