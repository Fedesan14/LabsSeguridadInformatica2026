#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
rotar-flags.py — rota las flags de los labs (herramienta del DOCENTE).

¿Para qué? Si alguien vio las soluciones (o simplemente querés flags nuevas por
cohorte), esto cambia el VALOR de cada flag y recalcula su hash en el manifest.
Quien conocía la flag vieja ya no puede entregarla: el hash no coincide.

Qué toca, sin romper nada:
  * Cada flag esta plantada en su target — en base64 (server.py/setup.sh),
    en claro (artefactos de forensia) o URL-encoded (access.log). El rotador
    detecta la codificacion y reemplaza respetandola.
  * Recalcula sha256(flag) en cada retos.manifest.
  * Lab 11 (forensia): recalcula la cadena de custodia (evidencia.sha256) para
    los archivos que cambian, PERO respeta el hash deliberadamente falso de
    auth.log — ese "fallo" de custodia ES el reto R5.
  * Deja el nuevo answer-key del docente en .soluciones-docente/ (gitignoreado).

SEGURIDAD: por defecto es DRY-RUN (solo muestra). Con --apply escribe.

Uso:
  bin/rotar-flags.py                 # dry-run, todos los labs reales
  bin/rotar-flags.py --lab 07        # dry-run, solo el lab 07
  bin/rotar-flags.py --apply         # aplica en todos
  bin/rotar-flags.py --lab 11 --apply
  bin/rotar-flags.py --random --apply   # flags opacas FLAG{<hex>} en vez de slug
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import re
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FLAG_RE = re.compile(r"FLAG\{[a-zA-Z0-9_]+\}")
B64_RE = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")
URLENC_RE = re.compile(r"FLAG%7[Bb][a-zA-Z0-9_]+%7[Dd]")

# Colores (si es TTY)
def _c(code: str) -> str:
    return code if sys.stdout.isatty() else ""
G, Y, R, DIM, RST, B = _c("\033[32m"), _c("\033[33m"), _c("\033[31m"), _c("\033[2m"), _c("\033[0m"), _c("\033[1m")


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def urlenc(s: str) -> str:
    # Como en access.log: solo las llaves van encodeadas, el slug queda en claro.
    return s.replace("{", "%7B").replace("}", "%7D")


def tracked_files(subdir: Path) -> list[Path]:
    rel = subdir.relative_to(REPO)
    out = subprocess.check_output(["git", "ls-files", str(rel)], cwd=REPO, text=True)
    return [REPO / line for line in out.splitlines() if line.strip()]


def candidatos_en_lab(lab_dir: Path) -> dict[str, str]:
    """Devuelve {sha256(flag): flag} para cada flag plantada en el lab, sin importar codificacion."""
    encontrados: dict[str, str] = {}
    for f in tracked_files(lab_dir):
        try:
            txt = f.read_text(errors="replace")
        except Exception:
            continue
        vistos: set[str] = set(FLAG_RE.findall(txt))
        for tok in set(B64_RE.findall(txt)):
            try:
                dec = base64.b64decode(tok, validate=True).decode("utf-8", "strict")
            except Exception:
                continue
            vistos.update(FLAG_RE.findall(dec))
        for tok in set(URLENC_RE.findall(txt)):
            vistos.update(FLAG_RE.findall(tok.replace("%7B", "{").replace("%7b", "{").replace("%7D", "}").replace("%7d", "}")))
        for fl in vistos:
            if fl not in ("FLAG{...}",):
                encontrados[sha256(fl)] = fl
    return encontrados


def parse_manifest(path: Path) -> list[tuple[int, str]]:
    """Devuelve [(nro_linea, contenido)] de las lineas de reto (no comentarios)."""
    lineas = []
    for i, ln in enumerate(path.read_text().splitlines()):
        if ln.strip() and not ln.lstrip().startswith("#") and "|" in ln:
            lineas.append((i, ln))
    return lineas


def nueva_flag(vieja: str, aleatoria: bool) -> str:
    if aleatoria:
        return "FLAG{" + secrets.token_hex(6) + "}"
    inner = vieja[len("FLAG{"):-1]
    # Si ya tenia sufijo de rotacion previo (_<6hex>), lo saco para no acumular.
    inner = re.sub(r"_[0-9a-f]{6}$", "", inner)
    return f"FLAG{{{inner}_{secrets.token_hex(3)}}}"


def reemplazar_en_texto(txt: str, vieja: str, nueva: str) -> tuple[str, list[str]]:
    """Reemplaza las 3 codificaciones posibles. Devuelve (texto_nuevo, [codifs_tocadas])."""
    tocadas = []
    for etq, ov, nv in (("claro", vieja, nueva), ("base64", b64(vieja), b64(nueva)), ("urlenc", urlenc(vieja), urlenc(nueva))):
        if ov in txt:
            txt = txt.replace(ov, nv)
            tocadas.append(etq)
    return txt, tocadas


def recalcular_custodia(lab_dir: Path, archivos_cambiados: set[Path]) -> list[str]:
    """Lab 11: reescribe evidencia.sha256 para los archivos cambiados, salvo auth.log (falso a proposito)."""
    custodia = lab_dir / "caso" / "evidencia.sha256"
    if not custodia.exists():
        return []
    caso = lab_dir / "caso"
    nuevas, notas = [], []
    for ln in custodia.read_text().splitlines():
        if not ln.strip():
            nuevas.append(ln)
            continue
        h, _, rel = ln.partition("  ")
        archivo = caso / rel
        if archivo in archivos_cambiados and "auth.log" not in rel:
            nh = hashlib.sha256(archivo.read_bytes()).hexdigest()
            nuevas.append(f"{nh}  {rel}")
            notas.append(f"custodia recalculada: {rel}")
        elif "auth.log" in rel and archivo in archivos_cambiados:
            nuevas.append(ln)  # se deja el hash FALSO: ese es el reto R5
            notas.append(f"custodia INTACTA (falsa a proposito): {rel}")
        else:
            nuevas.append(ln)
    custodia.write_text("\n".join(nuevas) + "\n")
    return notas


def labs_objetivo(filtro: str | None) -> list[Path]:
    todos = sorted(p.parent for p in REPO.glob("labs/*/retos.manifest"))
    todos = [p for p in todos if p.name != "_plantilla"]  # la plantilla es andamiaje
    if filtro and filtro != "all":
        todos = [p for p in todos if re.search(rf"lab0*{re.escape(filtro)}\b|{re.escape(filtro)}", p.name)]
    return todos


def main() -> int:
    ap = argparse.ArgumentParser(description="Rota las flags de los labs (docente).")
    ap.add_argument("--lab", default="all", help="numero de lab (ej: 07), 'final', o 'all'")
    ap.add_argument("--apply", action="store_true", help="escribir cambios (sin esto: dry-run)")
    ap.add_argument("--random", action="store_true", help="flags opacas FLAG{<hex>} en vez de slug+sufijo")
    args = ap.parse_args()

    labs = labs_objetivo(args.lab)
    if not labs:
        print(f"{R}No encontre labs para '{args.lab}'.{RST}")
        return 1

    print(f"{B}Rotador de flags{RST}  —  modo: {(R+'APLICAR'+RST) if args.apply else (Y+'DRY-RUN (no escribe)'+RST)}")
    print(f"{DIM}labs: {', '.join(p.name for p in labs)}{RST}\n")

    answer_key: list[str] = []
    total = 0
    for lab_dir in labs:
        manifest = lab_dir / "retos.manifest"
        por_hash = candidatos_en_lab(lab_dir)
        print(f"{B}{lab_dir.name}{RST}")
        cambios_manifest: list[tuple[str, str]] = []   # (hash_viejo, hash_nuevo)
        archivos_pendientes: dict[Path, str] = {}       # path -> texto nuevo acumulado
        archivos_cambiados: set[Path] = set()

        for _, linea in parse_manifest(manifest):
            rid, titulo, h = linea.split("|", 2)
            vieja = por_hash.get(h)
            if not vieja:
                print(f"  {Y}!{RST} {rid}: no pude ubicar la flag en claro (hash {h[:12]}...). La salteo.")
                continue
            nueva = nueva_flag(vieja, args.random)
            cambios_manifest.append((h, sha256(nueva)))
            answer_key.append(f"{lab_dir.name} {rid}  {nueva}")

            # Ubicar y preparar los archivos donde esta plantada
            sitios = []
            for f in tracked_files(lab_dir):
                if f.name == "retos.manifest":
                    continue
                base = archivos_pendientes.get(f)
                if base is None:
                    try:
                        base = f.read_text(errors="replace")
                    except Exception:
                        continue
                nuevo, tocadas = reemplazar_en_texto(base, vieja, nueva)
                if tocadas:
                    archivos_pendientes[f] = nuevo
                    archivos_cambiados.add(f)
                    sitios.append(f"{f.relative_to(lab_dir)} [{','.join(tocadas)}]")
            total += 1
            print(f"  {G}o{RST} {rid}: {DIM}{vieja}{RST} -> {G}{nueva}{RST}")
            for s in sitios:
                print(f"      {DIM}{s}{RST}")

        if args.apply:
            for f, txt in archivos_pendientes.items():
                f.write_text(txt)
            man_txt = manifest.read_text()
            for hv, hn in cambios_manifest:
                man_txt = man_txt.replace(hv, hn)
            manifest.write_text(man_txt)
            notas = recalcular_custodia(lab_dir, archivos_cambiados)
            for n in notas:
                print(f"      {DIM}{n}{RST}")
        print()

    print(f"{B}Total flags rotadas:{RST} {total}")
    if args.apply:
        # Guardar answer-key nuevo para el docente (fuera del repo del alumno)
        dest = REPO / ".soluciones-docente"
        dest.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        kf = dest / f"FLAGS-{ts}.txt"
        kf.write_text("# Answer-key generado por rotar-flags.py — NO subir al repo.\n"
                      + "\n".join(answer_key) + "\n")
        print(f"{G}Aplicado.{RST} Nuevo answer-key del docente: {DIM}{kf.relative_to(REPO)}{RST}")
        print(f"{Y}Recorda:{RST} reconstrui las imagenes Docker (make setup / rebuild) para que los targets sirvan las flags nuevas.")
    else:
        print(f"{Y}Dry-run.{RST} Volvé a correr con {B}--apply{RST} para escribir los cambios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
