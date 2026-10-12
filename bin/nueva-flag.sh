#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# nueva-flag.sh — helper para AUTORES de labs.
# Genera la línea de retos.manifest (id|titulo|sha256) a partir de una flag.
# Uso:  bin/nueva-flag.sh R1 "Titulo del reto" 'FLAG{lo_que_sea}'
set -euo pipefail
[ $# -eq 3 ] || { echo "Uso: $0 <id> <titulo> <FLAG{...}>"; exit 1; }
h="$(printf '%s' "$3" | shasum -a 256 | cut -d' ' -f1)"
echo "$1|$2|$h"
