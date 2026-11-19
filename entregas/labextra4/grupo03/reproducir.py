#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ejecuta el lab local y guarda salidas crudas y comandos reproducibles.

Desde la raíz: python -X utf8 entregas/labextra4/grupo03/reproducir.py
Reescribe evidencia; los tiempos nuevos pueden diferir del informe original.
Las flags se extraen de los loots descifrados y se entregan al CTF local.
"""
import argparse
import hashlib
import html
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SALIDAS = AQUI / "evidencia/salidas"
GRUPO = AQUI.relative_to(RAIZ).as_posix()
CASO = "labs/labextra4-cracking/caso"


def buscar_bash():
    if os.name != "nt":
        return shutil.which("bash")
    # Git Bash admite igncr para ejecutar el checkout con finales CRLF.
    git = shutil.which("git")
    if git:
        ruta = Path(git).resolve().parents[1] / "bin/bash.exe"
        if ruta.is_file():
            return str(ruta)
    return shutil.which("bash")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuar", action="store_true",
                        help="reutilizar las mediciones y ataques guardados; completar loot, CTF y captura")
    args = parser.parse_args()
    bash = buscar_bash()
    if not bash:
        raise SystemExit("Se necesita Bash (Git Bash en Windows) para ./ctf.")
    SALIDAS.mkdir(parents=True, exist_ok=True)
    entorno = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
    python = [sys.executable, "-X", "utf8"]
    ctf = ([bash, "-o", "igncr", f"{GRUPO}/ctf_windows.sh"] if os.name == "nt" else [bash, "./ctf"])
    comandos = AQUI / "evidencia/comandos.txt"
    with comandos.open("a" if args.continuar else "w", encoding="utf-8", newline="\n") as registro:
        registro.write("# Secuencia real ejecutada por reproducir.py; cwd = raíz del repositorio.\n")
        registro.write("# Python: modo UTF-8. CTF local: NO_COLOR=1. igncr solo en Git Bash/Windows por CRLF.\n")

        def ejecutar(argumentos, nombre, permitidos=(0,)):
            destino = SALIDAS / nombre
            linea = subprocess.list2cmdline(argumentos) if os.name == "nt" else shlex.join(argumentos)
            registro.write(f"{linea} > {destino.relative_to(RAIZ).as_posix()} 2>&1\n")
            registro.flush()
            print(f"Ejecutando: {nombre}", flush=True)
            with destino.open("wb") as salida:
                proceso = subprocess.run(argumentos, cwd=RAIZ, env=entorno, stdout=salida, stderr=subprocess.STDOUT)
            registro.write(f"# exit={proceso.returncode}\n")
            registro.flush()
            if proceso.returncode not in permitidos:
                raise RuntimeError(f"Falló {nombre}; consultar su salida cruda")
            return destino.read_text(encoding="utf-8")

        if args.continuar:
            for nombre in ("pruebas.txt", "mediciones.json", "diccionario.txt", "reglas.txt"):
                if not (SALIDAS / nombre).is_file():
                    raise RuntimeError(f"No se puede continuar: falta {nombre}")
            registro.write("# Continuación: se conservan las mediciones y ataques anteriores.\n")
            reglas = (SALIDAS / "reglas.txt").read_text(encoding="utf-8")
            anterior = SALIDAS / "submit-R1.txt"
            if anterior.is_file() and "[FAIL]" in anterior.read_text(encoding="utf-8"):
                shutil.copyfile(anterior, SALIDAS / "submit-R1-crlf.txt")
                registro.write("# Submit fallido archivado sin editar como submit-R1-crlf.txt (CRLF/llaves en Git Bash).\n")
            captura_anterior = SALIDAS / "captura.txt"
            if captura_anterior.is_file() and "FATAL" in captura_anterior.read_text(encoding="utf-8"):
                shutil.copyfile(captura_anterior, SALIDAS / "captura-intento1.txt")
                registro.write("# Captura fallida del navegador archivada sin editar como captura-intento1.txt.\n")
        else:
            ejecutar([*python, f"{GRUPO}/test_cracker.py"], "pruebas.txt")
            ejecutar([*python, f"{GRUPO}/medir.py", f"{CASO}/sombra.txt", f"{CASO}/diccionario.txt"], "mediciones.json")
            ejecutar([*python, f"{GRUPO}/cracker.py", "crackear", f"{CASO}/sombra.txt", f"{CASO}/diccionario.txt"], "diccionario.txt")
            reglas = ejecutar([*python, f"{GRUPO}/cracker.py", "crackear", f"{CASO}/sombra.txt", f"{CASO}/diccionario.txt", "--reglas"], "reglas.txt")
        halladas = dict(re.findall(r"^  ✓ ([^:]+): (.+)$", reglas, re.MULTILINE))
        if set(halladas) != {"operador", "analista", "admin"}:
            raise RuntimeError("Resultado inesperado: deben caer tres cuentas y root quedar sin coincidencia")
        for reto, usuario in zip(("R1", "R2", "R3"), ("operador", "analista", "admin")):
            loot = ejecutar([*python, f"{GRUPO}/cracker.py", "descifrar", f"{CASO}/loot/{usuario}.enc", "--password", halladas[usuario]], f"loot-{usuario}.txt")
            flag = re.search(r"FLAG\{[^}\r\n]+\}", loot)
            if not flag:
                raise RuntimeError(f"No hay flag en el loot de {usuario}")
            # Al lanzar MSYS desde Windows, las llaves pueden expandirse antes
            # de llegar a Bash. El CTF admite el cuerpo y agrega FLAG{...}.
            valor = flag.group()[5:-1] if os.name == "nt" else flag.group()
            ejecutar([*ctf, "submit", "extra4", reto, valor], f"submit-{reto}.txt")
        estado = ejecutar([*ctf, "status", "extra4"], "ctf-status.txt")
        if "3/3 (100%)" not in estado:
            raise RuntimeError("El CTF no acredita los tres retos")

        # La captura muestra la salida real en un visor HTML local, sin editarla.
        visor = AQUI / "evidencia/ctf-status.html"
        visor.write_text("<!doctype html><html lang='es'><meta charset='utf-8'>"
                         "<title>Salida real de ctf status extra4</title>"
                         "<style>body{background:#111;color:#eee;margin:32px}"
                         "pre{font:16px/1.6 Consolas,monospace;white-space:pre-wrap}"
                         "p{font:14px sans-serif;color:#bbb}</style>"
                         "<p>Lab Extra 4 · Grupo 03 · Visor de la salida cruda guardada en salidas/ctf-status.txt</p>"
                         "<pre>" + html.escape("$ ./ctf status extra4\n" + estado) + "</pre></html>", encoding="utf-8")
        navegadores = [shutil.which("chromium"), shutil.which("google-chrome"),
                       "C:/Program Files/Google/Chrome/Application/chrome.exe",
                       "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"]
        navegador = next((str(p) for p in navegadores if p and Path(p).is_file()), None)
        if navegador:
            with tempfile.TemporaryDirectory(prefix="labextra4-browser-", ignore_cleanup_errors=True) as perfil:
                ejecutar([navegador, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                          "--no-sandbox", "--disable-gpu-sandbox", "--disable-background-networking",
                          f"--user-data-dir={perfil}", "--window-size=1200,650", "--hide-scrollbars",
                          f"--screenshot={AQUI / 'evidencia/ctf-status.png'}", visor.as_uri()], "captura.txt")
            if not (AQUI / "evidencia/ctf-status.png").is_file():
                raise RuntimeError("El navegador no generó la captura")
        else:
            print("Sin navegador headless: abrir evidencia/ctf-status.html para capturar la salida.", flush=True)

    entradas = [f"{CASO}/sombra.txt", f"{CASO}/diccionario.txt",
                *(f"{CASO}/loot/{u}.enc" for u in ("operador", "analista", "admin")),
                "labs/labextra4-cracking/retos.manifest", "ctf", "bin/lib/check.sh", "bin/lib/ui.sh", "bin/lib/banner.sh"]
    (AQUI / "evidencia/entradas.sha256").write_text("".join(
        f"{hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest()}  {ruta}\n" for ruta in entradas), encoding="utf-8")
    print("Evidencia completa; CTF local: 3/3. Revisar los tiempos antes de actualizar el informe.", flush=True)


if __name__ == "__main__":
    main()
