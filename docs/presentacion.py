#!/usr/bin/env python3
"""
presentacion.py — CyberLab UTN · presentación de terminal (curses, bien hacker).

  ./docs/presentacion.py            interactiva (← → · espacio · p · g · q)
  ./docs/presentacion.py --no-intro sin lluvia de Matrix
  ./docs/presentacion.py --all      vuelca las slides como texto (sin curses)

Solo biblioteca estándar. La animación necesita una terminal real (TTY).
"""
import curses, locale, math, random, sys, time

def _put(stdscr, y, x, ch, attr):
    h, w = stdscr.getmaxyx()
    if 0 <= y < h and 0 <= x < w - 1:
        try: stdscr.addstr(y, x, ch, attr)
        except curses.error: pass

# ── paleta (índices de color-pair) ───────────────────────────────────────
G, C, A, V, W, D, R, H = 1, 2, 3, 4, 5, 6, 7, 8   # green cyan amber violet white dim red head

def _init_colors():
    curses.start_color()
    try: curses.use_default_colors(); bg = -1
    except curses.error: bg = curses.COLOR_BLACK
    curses.init_pair(G, curses.COLOR_GREEN, bg)
    curses.init_pair(C, curses.COLOR_CYAN, bg)
    curses.init_pair(A, curses.COLOR_YELLOW, bg)
    curses.init_pair(V, curses.COLOR_MAGENTA, bg)
    curses.init_pair(W, curses.COLOR_WHITE, bg)
    curses.init_pair(D, curses.COLOR_BLUE, bg)
    curses.init_pair(R, curses.COLOR_RED, bg)
    curses.init_pair(H, curses.COLOR_WHITE, bg)

def cp(k, bold=False):
    a = curses.color_pair(k)
    if bold or k in (H, G): a |= curses.A_BOLD if bold else 0
    return a

# ── contenido ────────────────────────────────────────────────────────────
COVER = [
 "  ██████╗██╗   ██╗██████╗ ███████╗██████╗     ██╗      █████╗ ██████╗",
 " ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██║     ██╔══██╗██╔══██╗",
 " ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██║     ███████║██████╔╝",
 " ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║     ██╔══██║██╔══██╗",
 " ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ███████╗██║  ██║██████╔╝",
 "  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═════╝",
]
FIN = [
 "  ███████╗██╗███╗   ██╗", "  ██╔════╝██║████╗  ██║", "  █████╗  ██║██╔██╗ ██║",
 "  ██╔══╝  ██║██║╚██╗██║", "  ██║     ██║██║ ╚████║", "  ╚═╝     ╚═╝╚═╝  ╚═══╝",
]
SKULL = [
 "        _.,----,._        ",
 "      .:'        `:.      ",
 "    .:'            `:.    ",
 "   ::                ::   ",
 "  ::    .-.    .-.    ::  ",
 "  ::   (o o)  (o o)   ::  ",
 "  ::    `-'    `-'    ::  ",
 "   ::        ^       ::   ",
 "    ::    .-===-.   ::    ",
 "     ::  ( |||| )  ::     ",
 "      `:.  `--'  .:'      ",
 "        `:.,__,.:'        ",
 "       |  |  |  |  |      ",
 "       '--'--'--'--'      ",
]

def L(*seg):  # una línea = lista de (texto, color)
    return list(seg)

SLIDES = [
 # 1 · cover
 {"center": True, "art": (COVER, G), "lines": [
   L(("", W)),
   L(("Práctico de Seguridad Informática — de la tríada CIA a los agentes", W)),
   L(("autónomos y de vuelta a la defensa. Diez labs + un engagement final.", W)),
   L(("", W)),
   L(("UTN · FRVM   /   Seguridad Informática   /   2026   /   ", D), ("Ing. Fernando Boiero", G)),
 ]},
 # 2
 {"kicker": "Qué es", "title": "Se aprende haciendo", "lines": [
   L(("No se aprende leyendo. Se opera con herramientas reales contra objetivos", W)),
   L(("deliberadamente vulnerables que se levantan solos en Docker.", W)),
   L(("", W)),
   L(("▸ ", G), ("Hands-on ", W), ("      todo con código, tool por tool, cada escenario", D)),
   L(("▸ ", C), ("Autodescubrible ", W), (" un comando ./ctf y el entorno arranca", D)),
   L(("▸ ", A), ("Progresivo ", W), ("    de la tríada CIA a agentes de IA y defensa", D)),
 ]},
 # 3
 {"kicker": "Filosofía · 4 reglas", "title": "Sin atajos", "lines": [
   L(("[01] ", G), ("Conceptos antes que código   ", W), ("primero el porqué, después la tool", D)),
   L(("[02] ", G), ("A mano antes que automático  ", W), ("los agentes recién al final", D)),
   L(("[03] ", G), ("La IA es una herramienta     ", W), ("el humano dirige, la máquina ejecuta", D)),
   L(("[04] ", G), ("Sin atajos                   ", W), ("nadie se hace pentester en dos horas", D)),
 ]},
 # 4
 {"kicker": "El programa · 10 labs + final", "lines": [
   L(("FUNDAMENTOS · CÓDIGO (Python)          ", G), ("OFENSIVA · Docker", C)),
   L(("┌─────────────────────────────┐    ┌─────────────────────────────┐", D)),
   L(("│ 01 Introducción (CIA, hash) │    │ 05 Reconocimiento           │", W)),
   L(("│ 02 Criptografía             │    │ 06 Enumeración              │", W)),
   L(("│ 03 Autenticación (2FA)      │    │ 07 Explotación              │", W)),
   L(("│ 04 Marcos normativos        │    │ 08 Post-explotación         │", W)),
   L(("│                             │    │ 09 Agentes de IA            │", W)),
   L(("│                             │    │ 10 Detección y evasión      │", W)),
   L(("└─────────────────────────────┘    └─────────────────────────────┘", D)),
   L(("", W)),
   L(("★ ", A), ("…y todo desemboca en el Práctico Final: engagement + informe.", W)),
 ]},
 # 5
 {"kicker": "Unidades 05–10 · la cadena", "title": "El engagement", "lines": [
   L(("[05]", G), ("─▶", D), ("[06]", G), ("─▶", D), ("[07]", G), ("─▶", D),
     ("[08]", G), ("─▶", D), ("[09]", V), ("─▶", D), ("[10]", A), ("══▶ ", D), ("★ FINAL", A)),
   L((" recon  enum  exploit  post  agentes defensa    informe", D)),
   L(("", W)),
   L(("Un hilo narrativo —la auditoría de PhantomCorp— atraviesa las seis unidades.", D)),
   L(("Manual (05–08) · Agentes (09) · Defensa (10). Cada lab avanza el ataque.", D)),
 ]},
 # 6
 {"kicker": "Cómo se juega", "lines": [
   L(("┌─ operador@cyberlab ───────────────────────────────┐", D)),
   L(("│ ", D), ("$ ./ctf lab 05", G), ("                                    │", D)),
   L(("│ ", D), ("  >> entorno arriba. entrá: make shell", D), ("       │", D)),
   L(("│ ", D), ("$ make shell", G), ("                                      │", D)),
   L(("│ ", D), ("attacker:~$ nmap -Pn phantomcorp", W), ("           │", D)),
   L(("│ ", D), ("  21/tcp open ftp  ProFTPD 1.3.5", D), ("           │", D)),
   L(("│ ", D), ("$ ./ctf submit 05 R1 'FLAG{...}'", G), ("            │", D)),
   L(("│ ", D), ("  ★ FLAG CAPTURADA · +1 al score", A), ("            │", D)),
   L(("└───────────────────────────────────────────────────┘", D)),
   L(("", W)),
   L(("Las flags te enganchan. ", W), ("El informe es lo que evalúa la rúbrica.", G)),
 ]},
 # 7
 {"kicker": "05–08 · a mano, siempre primero", "title": "El pentest, sin atajos", "lines": [
   L(("05 Reconocimiento   ", G), ("nmap, banners, headers, robots — mapear y clasificar", D)),
   L(("06 Enumeración      ", G), ("dirb, whatweb, .git expuesto, métodos HTTP, APIs", D)),
   L(("07 Explotación      ", G), ("SQLi real (sqlite+sqlmap), cmdi, traversal, IDOR", D)),
   L(("08 Post-explotación ", G), ("escalada por SUID, pivoting, automatización", D)),
 ]},
 # 8 · pivot
 {"kicker": "Pivoting · redes segmentadas (lab 08)", "lines": [
   L((" labnet ······························  internalnet ·········", D)),
   L(("┌────────────┐  HTTP   ┌────────────┐  pivot  ┌────────────┐", D)),
   L(("│ ", D), ("ATACANTE", W), ("   │────────▶│ ", D), ("VÍCTIMA", G), ("    │───────▶│ ", D), ("DB INTERNA", W), (" │", D)),
   L(("│ ", D), ("tu consola", D), (" │         │ ", D), ("2 redes", D), ("    │         │ ", D), ("crown", D), ("      │", D)),
   L(("└─────┬──────┘         └────────────┘         └─────▲──────┘", D)),
   L(("      ", D), (":  ✗ sin ruta directa — segmentado ", R), ("            │", D)),
   L(("      ", D), ("└──────────────────────────────────────────────┘", R)),
   L(("", W)),
   L(("El atacante no llega a la DB. La víctima vive en las dos redes: el trampolín.", D)),
 ]},
 # 9 · agente loop
 {"kicker": "Unidad 09 · Agentes de pentest", "lines": [
   L(("┌───────────┐ propone ┌───────────┐  ok  ┌───────────┐", D)),
   L(("│ ", D), ("LLM razona", W), ("│────────▶│ ", D), ("GUARDRAIL", V), (" │─────▶│ ", D), ("TOOL", W), ("      │", D)),
   L(("│ ", D), ("¿qué tool?", D), ("│         │ ", D), ("¿alcance?", D), (" │      │ ", D), ("nmap/curl", D), (" │", D)),
   L(("└─────▲─────┘         └─────┬─────┘      └─────┬─────┘", D)),
   L(("      ", D), ("│  resultado <~      ", G), ("│ ✗ fuera        ", A), ("│", G)),
   L(("      ", G), ("└───────────────────┴─────[ ", G), ("✗ BLOQUEA", A), (" ]", G)),
   L(("", W)),
   L(("El LLM razona; tu código pone las manos (tools) y los límites (guardrails).", D)),
   L(("Agnóstico: Claude · OpenAI · mock offline (corre sin API key).", D)),
 ]},
 # 10 · detección
 {"kicker": "Unidad 10 · Detección y evasión", "lines": [
   L(("?q=UNION SELECT      ──▶ ┌──────────┐ ──match──▶  ", W), ("[X] ALERTA", R)),
   L(("                        │ ", D), ("IDS·firma", C), (" │", D)),
   L(("?q=UNION/**/SELECT   ──▶ │ ", D), ("\\s+select", D), (" │ ─no match▶ ", D), ("✓ evadido", A)),
   L(("                        └──────────┘", D)),
   L(("", W)),
   L(("Del otro lado siempre hubo alguien mirando. Blue vs Red.", W)),
   L(("Mismo ataque: el espacio dispara la firma; un comentario /**/ la esquiva.", D)),
   L(("Lo que la firma no ve, lo caza el analista de logs. Ninguna es perfecta.", D)),
 ]},
 # 11 · final
 {"kicker": "★ Práctico Final · el engagement completo", "lines": [
   L(("[RECON]", G), ("─▶", D), ("[FOOTHOLD]", G), ("─▶", D), ("[LOOT]", G), ("─▶", D),
     ("[RCE]", G), ("─▶ ", D), ("[CROWN JEWELS]", A)),
   L((" 05·06     SQLi 07    token 08  cmd inj   datos de clientes", D)),
   L(("", W)),
   L(("Un solo objetivo que exige encadenar TODO el curso. Caja negra, 4 hitos.", W)),
   L(("El entregable estrella: ", A), ("informe de pentest profesional", W)),
   L(("(resumen ejecutivo + hallazgos con CVSS, evidencia y remediación).", D)),
 ]},
 # 12 · phantomcorp
 {"kicker": "El hilo narrativo · PhantomCorp S.A.", "lines": [
   L(("engagement.log", D)),
   L(("[05] perímetro mapeado ....... ", D), ("4 servicios", G)),
   L(("[06] intranet enumerada ...... ", D), (".git expuesto", G)),
   L(("[07] portal comprometido ..... ", D), ("RCE + SQLi", G)),
   L(("[08] root + red interna ...... ", D), ("pivot ok", G)),
   L(("[09] auditoría autónoma ...... ", D), ("agente", G)),
   L(("[10] visto por el SOC ........ ", D), ("firma evadida", G)),
   L(("[★ ] engagement final ........ ", D), ("informe entregado", A)),
 ]},
 # 13 · entrega
 {"kicker": "Cómo se entrega y se corrige", "lines": [
   L(("FLUJO", G), ("                             ", W), ("EVALUACIÓN", A)),
   L(("▸ fork + Pull Request (real)   ▸ rúbrica de 100 pts", W)),
   L(("▸ grupos 4–5 en entregas/      ▸ flags: pudiste · informe: entendiste", W)),
   L(("▸ los commits de todos cuentan ▸ uso de IA declarado (obligatorio)", W)),
   L(("", W)),
   L(("[!] Uso responsable. ", A), ("Solo contra los contenedores de la cátedra. Ley 26.388.", D)),
 ]},
 # 14 · fin
 {"center": True, "art": (SKULL, G), "lines": [
   L(("", W)),
   L(("El humano ", W), ("dirige", G), (". La máquina ejecuta.", W)),
   L(("La diferencia entre un pentester y un delincuente es la autorización,", D)),
   L(("el alcance y la ética. Nunca lo olvides.", D)),
   L(("", W)),
   L(("git clone", G), ("  ·  hacé el fork  ·  ponete las pilas", D)),
 ]},
]
N = len(SLIDES)

# ── lluvia de Matrix ─────────────────────────────────────────────────────
def matrix_rain(stdscr, seconds=2.6):
    h, w = stdscr.getmaxyx()
    chars = "01<>|/\\=+*[]{}#$%&@ABCDEF"
    drops = [random.randint(-h, 0) for _ in range(w)]
    stdscr.nodelay(True); stdscr.erase()
    end = time.time() + seconds
    while time.time() < end:
        for x in range(w):
            if random.random() < 0.45:
                continue
            y = drops[x]
            def putc(yy, ch, attr):
                if 0 <= yy < h and 0 <= x < w - 1:
                    try: stdscr.addstr(yy, x, ch, attr)
                    except curses.error: pass
            putc(y,     random.choice(chars), cp(H) | curses.A_BOLD)
            putc(y - 1, random.choice(chars), cp(G))
            putc(y - 4, random.choice(chars), cp(D))
            putc(y - 8, " ", curses.A_NORMAL)
            drops[x] = y + 1
            if drops[x] - 8 > h and random.random() < 0.08:
                drops[x] = 0
        stdscr.refresh()
        time.sleep(0.05)
        if stdscr.getch() != -1:
            break
    stdscr.nodelay(False); stdscr.erase()

# ── secuencia de arranque (fake boot) ────────────────────────────────────
def boot_sequence(stdscr):
    h, w = stdscr.getmaxyx()
    stdscr.erase(); stdscr.nodelay(True)
    logs = [
        ("cyberlab kernel 6.6.0-hardened  ...  boot", D),
        ("[  OK  ] montando /labs  (docker overlay)", G),
        ("[  OK  ] consola del atacante  (nmap · sqlmap · dirb)", G),
        ("[  OK  ] red segmentada  labnet / internalnet", G),
        ("[  OK  ] motor ctf  ·  verificador SHA-256", G),
        ("[ WARN ] toda accion queda registrada  —  Ley 26.388", A),
        ("estableciendo sesion segura", D),
    ]
    y = 2
    for text, col in logs:
        try: stdscr.addstr(y, 4, text, cp(col, bold=(col in (G, A))))
        except curses.error: pass
        y += 1; stdscr.refresh()
        if stdscr.getch() != -1: stdscr.nodelay(False); return
        time.sleep(0.14)
    # barra de progreso
    barw = min(46, w - 12); y += 1
    for f in range(barw + 1):
        fill = "#" * f + "." * (barw - f)
        pct = int(f * 100 / barw)
        try:
            stdscr.addstr(y, 4, "handshake [", cp(D))
            stdscr.addstr(y, 15, fill, cp(G, bold=True))
            stdscr.addstr(y, 15 + barw, f"] {pct:3d}%", cp(D))
        except curses.error: pass
        stdscr.refresh()
        if stdscr.getch() != -1: break
        time.sleep(0.012)
    try:
        stdscr.addstr(y + 2, 4, ">> ACCESS GRANTED", cp(G, bold=True) | curses.A_BLINK)
    except curses.error: pass
    stdscr.refresh(); time.sleep(0.55)
    stdscr.nodelay(False); stdscr.erase()

# ── radar / sonar (escena "escaneando") ──────────────────────────────────
# Velocidad del radar (ajustá acá):
RADAR_SWEEPS = 2        # cuántas vueltas completas da el haz
RADAR_DELAY  = 0.020    # segundos por cuadro — MÁS chico = MÁS rápido; MÁS grande = MÁS lento
RADAR_STEPS  = 56       # cuadros por vuelta — MÁS chico = giro más veloz

def radar_scan(stdscr, sweeps=RADAR_SWEEPS):
    h, w = stdscr.getmaxyx()
    cy, cx = h // 2, max(10, w // 2 - 8)
    r = max(5, min(h // 2 - 3, w // 4 - 6))
    rnd = random.Random(1337)
    targets = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0.35, 0.92)) for _ in range(6)]
    primary = targets[2]
    stdscr.nodelay(True)
    steps = RADAR_STEPS
    for t in range(sweeps * steps + 1):
        ang = (t % steps) / steps * 2 * math.pi
        vueltas = t / steps
        stdscr.erase()
        for rf in (1.0, 0.66, 0.33):                     # anillos
            rr = r * rf
            for d in range(0, 360, 4):
                a = math.radians(d)
                _put(stdscr, cy + int(rr * math.sin(a)), cx + int(2 * rr * math.cos(a)), ".", cp(D))
        _put(stdscr, cy, cx, "+", cp(G, True))            # centro
        for k in range(0, 7):                             # barrido con estela
            a = ang - k * 0.055
            col = H if k == 0 else (G if k < 3 else D)
            ch = "*" if k == 0 else "/"
            for rr in range(1, r):
                _put(stdscr, cy + int(rr * math.sin(a)), cx + int(2 * rr * math.cos(a)), ch, cp(col, k == 0))
        for i, (ta, td) in enumerate(targets):            # blips
            bx = cx + int(2 * (td * r) * math.cos(ta)); by = cy + int((td * r) * math.sin(ta))
            lit = ((ang - ta) % (2 * math.pi)) < 0.55
            if (ta, td) == primary and vueltas >= 1:
                _put(stdscr, by, bx, "O", cp(A, True))
                _put(stdscr, by, bx + 2, "phantomcorp", cp(A, True))
            else:
                _put(stdscr, by, bx, "O" if lit else "o", cp(G if lit else D, lit))
        locked = vueltas >= 1.5
        _put(stdscr, 1, 3, "[ TARGET LOCKED ]  phantomcorp" if locked else "[ SCANNING PERIMETER ]  buscando objetivos...",
             cp(A if locked else G, True))
        _put(stdscr, h - 2, 3, f"hosts detectados: {len(targets)}   ·   sweep {int(vueltas)+1}/{sweeps}", cp(D))
        stdscr.refresh()
        if stdscr.getch() != -1: break
        time.sleep(RADAR_DELAY)
    time.sleep(0.35)
    stdscr.nodelay(False); stdscr.erase()

# ── firewall vulnerado · candado que se abre ─────────────────────────────
PADLOCK_CLOSED = [
    r"     _____     ",
    r"    /     \    ",
    r"   |       |   ",
    r"   |       |   ",
    r" __|       |__ ",
    r"|             |",
    r"|    _____    |",
    r"|   |     |   |",
    r"|   | (o) |   |",
    r"|   |_____|   |",
    r"|             |",
    r"|_____________|",
]
PADLOCK_OPEN = [
    r"     _____     ",
    r"    /     \____",
    r"   |          |",
    r"   |           ",
    r" __|           ",
    r"|             |",
    r"|    _____    |",
    r"|   |     |   |",
    r"|   | (o) |   |",
    r"|   |_____|   |",
    r"|             |",
    r"|_____________|",
]

def firewall_breach(stdscr, seconds=4.2):
    h, w = stdscr.getmaxyx()
    stdscr.nodelay(True)
    lw = max(len(l) for l in PADLOCK_CLOSED)
    lh = len(PADLOCK_CLOSED)
    py = max(2, h // 2 - lh // 2)
    def puts(y, x, s, attr):
        for j, ch in enumerate(s):
            _put(stdscr, y, x + j, ch, attr)
    def draw_wall(crack):
        row = "[==]" * (w // 4 + 2)
        for y in range(h):
            off = (y % 2) * 2
            line = row[off:off + w]
            for x, ch in enumerate(line):
                if crack and random.random() < crack:
                    continue
                _put(stdscr, y, x, ch, cp(D))
    def draw_lock(art, color, jit=0):
        px = (w - lw) // 2 + jit
        for i in range(lh):                      # foco: limpia la caja
            puts(py + i, px - 1, " " * (lw + 2), curses.A_NORMAL)
        for i, line in enumerate(art):
            puts(py + i, px, line, cp(color, True))
    steps = int(seconds / 0.05)
    for t in range(steps):
        pr = t / steps
        stdscr.erase()
        draw_wall(0.0 if pr < 0.75 else (pr - 0.75) * 1.4)
        if pr < 0.78:
            jit = random.choice([-1, 0, 0, 1]) if pr > 0.28 else 0
            blink = R if int(t * 0.5) % 2 else A
            draw_lock(PADLOCK_CLOSED, blink, jit)
            puts(1, 3, f"[ BREACHING FIREWALL ]  intento {int(pr * 99999):05d}", cp(R, True))
            barw = min(40, w - 16); f = int(pr / 0.78 * barw)
            puts(h - 2, 3, "brute-force [" + "#" * f + "-" * (barw - f) + "]", cp(A))
        else:
            draw_lock(PADLOCK_OPEN, G, 0)
            puts(1, 3, "[ FIREWALL BREACHED ]  candado abierto — ACCESS", cp(G, True))
            puts(h - 2, 3, "handshake ok · perimetro superado", cp(G))
        stdscr.refresh()
        if stdscr.getch() != -1: break
        time.sleep(0.05)
    time.sleep(0.5)
    stdscr.nodelay(False); stdscr.erase()

# ── calavera · SYSTEM PWNED ──────────────────────────────────────────────
def skull_scene(stdscr):
    h, w = stdscr.getmaxyx()
    sw = max(len(l) for l in SKULL); sh = len(SKULL)
    x0 = max(1, (w - sw) // 2); y0 = max(0, (h - sh) // 2 - 1)
    stdscr.nodelay(True)
    for f in range(9):                        # la calavera se decodea desde el ruido
        p = f / 8
        stdscr.erase()
        for i, line in enumerate(SKULL):
            _put_str(stdscr, y0 + i, x0, line if p >= 1 else _scr(line, p), cp(G, True))
        stdscr.refresh()
        if stdscr.getch() != -1: break
        time.sleep(0.05)
    msg = "S Y S T E M   P W N E D"
    sub = "root@phantomcorp:~# whoami  ->  root"
    for b in range(7):                        # parpadeo rojo/ambar
        for i, line in enumerate(SKULL):
            _put_str(stdscr, y0 + i, x0, line, cp(G, True))
        _put_str(stdscr, y0 + sh + 1, max(1, (w - len(msg)) // 2), msg, cp(R if b % 2 == 0 else A, True))
        _put_str(stdscr, y0 + sh + 2, max(1, (w - len(sub)) // 2), sub, cp(D))
        stdscr.refresh()
        if stdscr.getch() != -1: break
        time.sleep(0.16)
    stdscr.nodelay(False); stdscr.erase()

# ── efecto "desencriptado" de un bloque ASCII ────────────────────────────
def decrypt_reveal(stdscr, art, y0, col, w, center, m, frames=13):
    noise = "01<>|/\\=+*#$%&@ABCDEF#*+.:"
    stdscr.nodelay(True)
    for f in range(frames + 1):
        pr = f / frames
        for r, line in enumerate(art):
            out = []
            for ch in line:
                if ch == " ":
                    out.append(" ")
                elif random.random() < pr:
                    out.append(ch)
                else:
                    out.append(random.choice(noise))
            s = "".join(out)
            x = max(2, (w - len(s)) // 2) if center else m
            try: stdscr.addstr(y0 + r, x, s, cp(col, bold=True))
            except curses.error: pass
        stdscr.refresh()
        if stdscr.getch() != -1:
            break
        time.sleep(0.045)
    stdscr.nodelay(False)

# ── dibujo de una slide ──────────────────────────────────────────────────
NOISE = "01<>|/=+*#$%&@ABCDEFabcdef#*+."

def _scr(t, p):    # scramble: cada char es final (prob p) o ruido
    return "".join(c if (c == " " or random.random() < p) else random.choice(NOISE) for c in t)

def _put_str(stdscr, y, x, s, attr):
    h, w = stdscr.getmaxyx()
    if 0 <= y < h and 0 <= x < w - 1:
        try: stdscr.addstr(y, x, s[:w - 1 - x], attr)
        except curses.error: pass

def _footer(idx):
    return [(f"[{idx+1:02d}/{N}]  ", D), ("← →/espacio", G), (" avanzar · ", D),
            ("p", G), (" atrás · ", D), ("g", G), (" ir · ", D), ("q", R), (" salir", D)]

def _layout(stdscr, idx):
    h, w = stdscr.getmaxyx()
    s = SLIDES[idx]; center = s.get("center", False)
    m = max(3, (w - 74) // 2) if not center else 2
    ops = []; y = 2
    if s.get("kicker"):
        ops.append((y, m, [("// " + s["kicker"], G)])); y += 2
    if s.get("art"):
        art, col = s["art"]
        for line in art:
            x = max(2, (w - len(line)) // 2) if center else m
            ops.append((y, x, [(line, col)])); y += 1
        y += 1
    elif s.get("title"):
        ops.append((y, m, [("» " + s["title"], W)])); y += 2
    for line in s["lines"]:
        x = max(2, (w - sum(len(t) for t, _ in line)) // 2) if center else m
        ops.append((y, x, line)); y += 1
    return ops, h, w

def _paint(stdscr, ops, h, idx, p=1.0):
    stdscr.erase()
    for y, x, segs in ops:
        xx = x
        for text, color in segs:
            t = text if p >= 1.0 else _scr(text, p)
            _put_str(stdscr, y, xx, t, cp(color, bold=(color in (G, H, A))))
            xx += len(text)
    fx = 2
    for text, color in _footer(idx):
        _put_str(stdscr, h - 1, fx, text, cp(color, bold=(color in (G, H, A)))); fx += len(text)
    stdscr.refresh()

def draw_slide(stdscr, idx, animate=False, frames=9):
    ops, h, w = _layout(stdscr, idx)
    if not animate:
        _paint(stdscr, ops, h, idx, 1.0); return
    stdscr.nodelay(True)                       # efecto "decode": ruido -> texto
    for f in range(frames + 1):
        p = f / frames
        _paint(stdscr, ops, h, idx, p)
        if p < 1.0:
            k = stdscr.getch()
            if k != -1:                        # tecla = saltar animación y no perder el input
                _paint(stdscr, ops, h, idx, 1.0)
                try: curses.ungetch(k)
                except curses.error: pass
                break
            time.sleep(0.03)
    stdscr.nodelay(False)

def goto_prompt(stdscr):
    h, w = stdscr.getmaxyx()
    curses.echo(); curses.curs_set(1)
    try:
        stdscr.addstr(h - 1, 2, " " * (w - 3))
        stdscr.addstr(h - 1, 2, "ir a slide #: ", cp(G))
        s = stdscr.getstr(h - 1, 16, 3).decode(errors="ignore")
    except curses.error:
        s = ""
    curses.noecho(); curses.curs_set(0)
    return int(s) - 1 if s.strip().isdigit() else None

def run(stdscr, intro=True):
    curses.curs_set(0); _init_colors()
    if intro:
        try:
            boot_sequence(stdscr)          # logs de arranque + ACCESS GRANTED
            radar_scan(stdscr)             # radar barriendo -> TARGET LOCKED
            firewall_breach(stdscr)        # candado que se abre -> FIREWALL BREACHED
            skull_scene(stdscr)            # calavera -> SYSTEM PWNED
            matrix_rain(stdscr, 1.8)       # lluvia de Matrix
        except curses.error: pass
    i = 0
    show = lambda j: draw_slide(stdscr, j, animate=True)   # cada slide "decodea" al entrar
    show(0)
    while True:
        k = stdscr.getch()
        if k in (ord("q"), ord("Q")):
            break
        elif k in (curses.KEY_RIGHT, ord(" "), ord("n"), ord("j"), curses.KEY_DOWN, curses.KEY_NPAGE):
            i = min(N - 1, i + 1); show(i)
        elif k in (curses.KEY_LEFT, ord("p"), ord("b"), ord("k"), curses.KEY_UP, curses.KEY_PPAGE):
            i = max(0, i - 1); show(i)
        elif k in (ord("g"), ord("G")):
            n = goto_prompt(stdscr)
            if n is not None and 0 <= n < N:
                i = n
            show(i)
        elif k == curses.KEY_RESIZE:
            draw_slide(stdscr, i)

def dump():
    for idx, s in enumerate(SLIDES):
        print("\n" + "=" * 74)
        if s.get("kicker"): print("// " + s["kicker"])
        for line in s.get("art", ([], 0))[0]:
            print(line)
        if s.get("title"): print("» " + s["title"])
        for line in s["lines"]:
            print("".join(t for t, _ in line))

def main():
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    if "--all" in sys.argv:
        dump(); return
    intro = "--no-intro" not in sys.argv
    if not sys.stdout.isatty():
        print("Esta presentación necesita una terminal real. Probá --all para volcar el texto.")
        return
    try:
        curses.wrapper(run, intro=intro)
    except KeyboardInterrupt:
        pass
    print("root@cyberlab:~# ./fin.sh — hasta la próxima, loco.")

if __name__ == "__main__":
    main()
