#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
# validar-repo.sh — chequeos de salud del repositorio.
# Lo corre el CI en cada PR/push y lo podés correr a mano:  ./bin/validar-repo.sh
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
errores=0
fail() { echo "  ✗ $1"; errores=$((errores+1)); }
ok()   { echo "  ✓ $1"; }

echo "== 1. Python compila =="
while IFS= read -r f; do
  python3 -m py_compile "$f" 2>/dev/null || fail "no compila: $f"
done < <(find labs docs bin -name "*.py" 2>/dev/null)
[ "$errores" -eq 0 ] && ok "todos los .py compilan"

echo "== 2. Shell con sintaxis válida =="
antes=$errores
for f in ctf bin/nueva-flag.sh bin/lib/*.sh labs/*/start.sh; do
  [ -f "$f" ] && { bash -n "$f" 2>/dev/null || fail "sintaxis rota: $f"; }
done
[ "$errores" -eq "$antes" ] && ok "todos los scripts shell OK"

echo "== 3. Manifiestos de retos bien formados =="
antes=$errores
for m in labs/lab*/retos.manifest; do
  [ -f "$m" ] || continue
  # cada línea de reto: <ID>|<título>|<64 hex>   (IDs: R1.. o D1.., etc.)
  while IFS= read -r linea; do
    case "$linea" in ''|\#*) continue;; esac
    echo "$linea" | grep -qE '^[A-Za-z]+[0-9]+\|[^|]+\|[0-9a-f]{64}$' \
      || fail "$m: línea mal formada: ${linea:0:40}..."
  done < "$m"
done
[ "$errores" -eq "$antes" ] && ok "todos los retos.manifest OK"

echo "== 4. Sin soluciones en el repo (H1) =="
encontradas="$(find labs -name 'solucion.md' 2>/dev/null)"
if [ -n "$encontradas" ]; then
  fail "solucion.md versionado (va solo en tu copia local .soluciones-docente/): $encontradas"
else
  ok "no hay solucion.md versionados"
fi

echo "== 5. Sin flags REALES en claro en documentación pública =="
# Las flags viven base64 en los targets. Una flag solo es un problema si es
# REAL: su SHA-256 figura en algún retos.manifest. Flags de ejemplo
# (FLAG{ejemplo_...}) son didácticas y no se reportan.
antes=$errores
while IFS= read -r f; do
  fail "flag REAL en claro en doc público: $f"
done < <(python3 - <<'PY'
import hashlib, re, pathlib
# hashes de todas las flags reales del curso
reales = set()
for man in pathlib.Path('labs').glob('lab*/retos.manifest'):
    for linea in man.read_text(errors='ignore').splitlines():
        if linea.startswith('R'):
            reales.add(linea.split('|')[2].strip())
# flags literales en docs públicos
rutas = ([pathlib.Path('README.md'), pathlib.Path('CONTRIBUTING.md')]
         + list(pathlib.Path('docs').glob('*.md'))
         + list(pathlib.Path('labs').glob('lab*/README.md'))
         + list(pathlib.Path('labs').glob('lab*/docs/*.md')))
for md in rutas:
    if not md.exists() or 'entregable' in md.name: continue
    for flag in re.findall(r'FLAG\{[^}\s]+\}', md.read_text(errors='ignore')):
        if hashlib.sha256(flag.encode()).hexdigest() in reales:
            print(f"{md}: {flag}")
PY
)
[ "$errores" -eq "$antes" ] && ok "ninguna flag real en claro en documentación pública"

echo "== 6. Links internos entre .md =="
antes=$errores
while IFS= read -r f; do
  fail "link interno roto: $f"
done < <(python3 - <<'PY'
import re, pathlib
for md in pathlib.Path('.').rglob('*.md'):
    if '.git' in md.parts: continue
    for m in re.finditer(r'\[[^\]]*\]\(([^)#\s]+)(#[^)]*)?\)', md.read_text(errors='ignore')):
        url = m.group(1)
        if url.startswith(('http://','https://','mailto:')): continue
        if not (md.parent / url).resolve().exists():
            print(f"{md}: {url}")
PY
)
[ "$errores" -eq "$antes" ] && ok "links internos OK"

echo
if [ "$errores" -gt 0 ]; then
  echo "VALIDACIÓN: $errores problema(s) encontrados."
  exit 1
fi
echo "VALIDACIÓN: todo OK."
