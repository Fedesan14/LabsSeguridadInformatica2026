#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Compatibilidad con el checkout CRLF en Git Bash, sin editar la cátedra.
# Uso desde la raíz: bash -o igncr entregas/labextra4/grupo03/ctf_windows.sh status extra4
set -euo pipefail

# igncr corrige la lectura del código Bash, pero no el CR final que grep
# devuelve al leer retos.manifest como datos. Ese CR falsea la comparación
# con sha256(flag). Se conserva el estado de grep mediante pipefail.
grep() { command grep "$@" | tr -d '\r'; }
export -f grep

exec bash -o igncr ./ctf "$@"
