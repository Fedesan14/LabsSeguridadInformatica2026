#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp SOC — target del Lab 10 (Detección y evasión).

Del otro lado del ataque hay un defensor. Este servicio es una app MONITOREADA:
inspecciona cada request contra firmas de detección (como un IDS/WAF ingenuo) y
lleva un log tipo SOC. Vas a: (1) ver cómo te detectan, (2) entender las firmas,
(3) EVADIRLAS, y (4) encontrar una intrusión real escondida en el ruido.

La lección: la detección por firmas es poderosa pero frágil. El que entiende la
firma, la esquiva. Y el que analiza logs, encuentra lo que la firma no vio.
"""
import base64, re
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_SOC     = _f("RkxBR3tzb2NfbG9nX2FjY2Vzc30=")
FLAG_DETECT  = _f("RkxBR3tkZXRlY3Rpb25fdHJpZ2dlcmVkfQ==")
FLAG_RULES   = _f("RkxBR3tzaWduYXR1cmVfcnVsZXNldH0=")
FLAG_EVADE   = _f("RkxBR3tzaWduYXR1cmVfZXZhZGVkfQ==")
FLAG_INTRUS  = _f("RkxBR3tpbnRydXNpb25faW5fdGhlX25vaXNlfQ==")

# Firmas de detección (ingenuas a propósito)
FIRMAS = [
    ("scanner-ua",     lambda path, q, ua: bool(re.search(r"sqlmap|nikto|nmap|dirb", ua, re.I))),
    ("path-traversal", lambda path, q, ua: "../" in path or "../" in q),
    ("git-probe",      lambda path, q, ua: "/.git" in path),
    ("sqli-union",     lambda path, q, ua: bool(re.search(r"union\s+select", q, re.I))),  # requiere ESPACIO
]

def _log_soc() -> str:
    lineas = []
    for i in range(1, 121):
        ip = f"10.0.{i % 6}.{20 + i % 40}"
        lineas.append(f"{ip} - GET /catalogo?item={i} 200 BENIGN")
        if i == 73:  # intrusión real escondida en el ruido (NO es del alumno)
            lineas.append(f"185.220.101.42 - GET /admin/../../etc/passwd 200 ALERT[path-traversal] "
                          f"# intrusion no atribuida -> {FLAG_INTRUS}")
    cab = (f"=== PhantomCorp SOC · vista de eventos ===\n"
           f"Acceso a la consola del SOC concedido. {FLAG_SOC}\n"
           f"Tip: filtrá por ALERT. Hay UNA intrusion real que no disparaste vos.\n"
           f"{'-'*60}\n")
    return cab + "\n".join(lineas) + "\n"

REGLAS_TXT = (
    "=== Ruleset del IDS (firmas activas) ===\n"
    f"Conocer las reglas es el primer paso para evadirlas. {FLAG_RULES}\n"
    "  scanner-ua      User-Agent contiene sqlmap|nikto|nmap|dirb\n"
    "  path-traversal  la ruta contiene '../'\n"
    "  git-probe       la ruta contiene '/.git'\n"
    "  sqli-union      el query matchea /union\\s+select/  (OJO: exige un ESPACIO)\n"
    "\nUna firma que exige un espacio se esquiva quitando el espacio. Pensá.\n"
)

class H(BaseHTTPRequestHandler):
    server_version = "PhantomSOC/1.0"; sys_version = ""
    def log_message(self, *a): pass
    def _txt(self, code, body):
        if isinstance(body, str): body = body.encode()
        self.send_response(code); self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        u = urlparse(self.path); path = u.path.rstrip("/"); q = u.query
        ua = self.headers.get("User-Agent", "")
        # rutas del SOC (no se inspeccionan como ataque)
        if path == "/soc":         return self._txt(200, _log_soc())
        if path == "/soc/reglas":  return self._txt(200, REGLAS_TXT)
        # inspección IDS
        for nombre, fn in FIRMAS:
            if fn(path, q, ua):
                return self._txt(403, f"🚨 ALERTA IDS · firma '{nombre}' disparada.\n"
                                      f"Tu request fue DETECTADA y logueada. {FLAG_DETECT}\n"
                                      f"Para ver todas las reglas: GET /soc/reglas\n")
        # ataque REAL que evadió las firmas (union+select sin el espacio exacto)
        low = q.lower()
        if "union" in low and "select" in low:
            return self._txt(200, f"200 OK (procesado como benigno)\n"
                                  f"Tu request ERA maliciosa pero NINGUNA firma la detectó. {FLAG_EVADE}\n")
        if path == "" or self.path == "/":
            return self._txt(200, "PhantomCorp — portal monitoreado. Del otro lado hay un SOC mirando.\n")
        self._txt(200, "200 OK BENIGN\n")

if __name__ == "__main__":
    print("[phantomcorp-soc] arriba en :80 (monitoreado)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
