#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
intro-clase.py — intro CORTA para abrir la clase de hoy y soltarlos a trabajar.

Reusa el motor de presentacion.py (matrix, radar, firewall, calavera, decode) —
solo cambia las slides. 6 diapositivas: bienvenida, novedades, cómo trabajan,
un lab en 4 comandos, cómo bajar lo nuevo, y "a trabajar".

    ./docs/intro-clase.py             (con la intro cinematográfica)
    ./docs/intro-clase.py --no-intro  (directo a las slides)
    ./docs/intro-clase.py --all       (texto plano)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presentacion as P
L = P.L
G, C, A, V, W, D = P.G, P.C, P.A, P.V, P.W, P.D

P.SLIDES = [
    # 1 · bienvenida
    {"center": True, "art": (P.COVER, G), "lines": [
        L(("", W)),
        L(("Seguridad Informática · UTN FRVM · clase de hoy", W)),
        L(("Novedades del práctico + cómo van a trabajar. Y después, al teclado.", D)),
    ]},
    # 2 · novedades
    {"kicker": "NOVEDADES · desde la clase pasada (04/09)", "lines": [
        L(("El repo creció. Nada de lo que ya hiciste cambia — es TODO sumado.", W)),
        L(("", W)),
        L(("1  ", G), ("Presentación de TERMINAL (esta) — matrix, radar, calavera, decode.", D)),
        L(("2  ", G), ("Guía dinámica de las 11 clases (gancho + ejemplo + dato hacker).", D)),
        L(("3  ", G), ("Banco de ~30 retos bonus con más tools (★/★★/★★★) por lab.", D)),
        L(("4  ", G), ("Lab 11 NUEVO — Forensia (DFIR): de atacar a investigar.", D)),
        L(("5  ", G), ("timeline.py — reconstruís la línea de tiempo del ataque.", D)),
    ]},
    # 3 · cómo se trabaja
    {"kicker": "Cómo se trabaja — en TODOS los prácticos", "lines": [
        L(("1  ", G), ("LEÉ el README del lab (Teoría → Ejemplos → Tools → Práctica).", D)),
        L(("2  ", G), ("HACÉ el lab: código (Python) · ofensivo (./ctf) · forensia (evidencia).", D)),
        L(("3  ", G), ("CAPTURÁ las flags — pero el INFORME es lo que evalúa la rúbrica.", D)),
        L(("4  ", G), ("ENTREGÁ por fork + Pull Request en entregas/labNN/grupoXX/.", D)),
        L(("5  ", G), ("BONUS (opcional): los retos extra, donde te hacés bueno de verdad.", D)),
        L(("", W)),
        L(("Todo SOLO contra los contenedores de la cátedra. Ley 26.388.", A)),
    ]},
    # 4 · un lab en 4 comandos
    {"kicker": "Un lab ofensivo, en 4 comandos", "lines": [
        L(("$ make setup", G), ("        una vez (arma la consola con las tools)", D)),
        L(("$ ./ctf lab 11", G), ("       levanta el lab y abre la guía", D)),
        L(("$ make shell", G), ("         entrás a la consola del atacante", D)),
        L(("$ ./ctf submit 11 R1 'FLAG{...}'", G), ("   entregás cada flag", D)),
        L(("", W)),
        L(("Los de código (01-04) se resuelven en Python. La forensia (11), sobre archivos.", D)),
    ]},
    # 5 · bajar lo nuevo
    {"kicker": "Antes de arrancar: bajá lo nuevo", "lines": [
        L(("Sincronizá tu fork con el repo de la cátedra (upstream):", W)),
        L(("", W)),
        L(("  git checkout main", C)),
        L(("  git fetch upstream", C)),
        L(("  git merge upstream/main", C)),
        L(("  git push origin main", C)),
        L(("", W)),
        L(("¿Sin upstream? ", D), ("git remote add upstream <repo-de-la-cátedra>", C)),
    ]},
    # 6 · a trabajar
    {"center": True, "art": (P.SKULL, G), "lines": [
        L(("", W)),
        L((">>>  A   T R A B A J A R  <<<", A)),
        L(("", W)),
        L(("Hoy: sincronizá, leé docs/INTRODUCCION.md, y encará el Lab 11 (Forensia).", W)),
        L(("¿Ya terminaste? A los retos bonus. Ponete las pilas.", D)),
        L(("", W)),
        L(("Dudas → un Issue en el repo. Dale que arrancamos.", G)),
    ]},
]
P.N = len(P.SLIDES)

if __name__ == "__main__":
    P.main()
