#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp Clientes — target del PRACTICO FINAL (engagement integrador).

Una sola caja que exige encadenar TODO el curso:
  recon/enum -> portal oculto -> SQLi (foothold) -> loot de token -> RCE (impacto).
Cuatro hitos, cada uno habilita el siguiente. Backend sqlite real.
"""
import base64, json, os, sqlite3
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_RECON = _f("RkxBR3tmaW5hbF9yZWNvbl9wb3J0YWx9")
FLAG_FOOT  = _f("RkxBR3tmaW5hbF9zcWxpX2Zvb3Rob2xkfQ==")
FLAG_TOKEN = _f("RkxBR3tmaW5hbF90b2tlbl9sb290ZWR9")
FLAG_CROWN = _f("RkxBR3tmaW5hbF9jcm93bl9qZXdlbHN9")
API_TOKEN = "phantom-api-7c1e"

os.makedirs("/app/priv", exist_ok=True)
open("/app/priv/clientes.db.txt", "w").write(
    "clientes: 48210 registros (nombre, DNI, tarjeta). " + FLAG_CROWN + "\n")

DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE users(user TEXT, pass TEXT, rol TEXT)")
DB.execute("INSERT INTO users VALUES('admin','no-adivinable-9931','admin')")
DB.commit()

PORTAL_HTML = ("<!doctype html><title>Portal RRHH PhantomCorp</title>"
               "<h1>Portal interno RRHH</h1><form method=post action=/portal/login>"
               "<input name=user><input name=pass type=password></form>"
               f"<!-- recon: portal interno localizado. {FLAG_RECON} -->").encode()

class H(BaseHTTPRequestHandler):
    server_version = "PhantomClientes/2.0"; sys_version = ""
    def log_message(self, *a): pass
    def _s(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str): body = body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        u = urlparse(self.path); p = u.path.rstrip("/"); q = parse_qs(u.query)
        if self.path == "/" or p == "":
            self._s(200, "<h1>PhantomCorp Clientes</h1><p>Portal publico.</p>")
        elif p == "/robots.txt":
            self._s(200, "User-agent: *\nDisallow: /portal-rrhh\n", "text/plain")
        elif p == "/portal-rrhh":
            self._s(200, PORTAL_HTML)
        elif p == "/backup/rrhh.conf":
            # loot: aparece en el dashboard tras el foothold
            self._s(200, f"DB_USER=rrhh_app\nDB_PASS=Rh-2026\nAPI_TOKEN={API_TOKEN}\n"
                         f"# usar el token en /api/reporte?token=...&cmd=... {FLAG_TOKEN}\n", "text/plain")
        elif p == "/api/reporte":
            # RCE gateado por el token looteado
            if q.get("token", [""])[0] != API_TOKEN:
                return self._s(403, "token invalido; conseguilo del backup de RRHH", "text/plain")
            cmd = q.get("cmd", ["id"])[0]
            out = os.popen(cmd).read()   # command injection deliberada
            self._s(200, f"$ {cmd}\n{out}", "text/plain")
        else:
            self._s(404, "Not Found")
    def do_POST(self):
        u = urlparse(self.path)
        if u.path.rstrip("/") == "/portal-rrhh/login" or u.path.rstrip("/") == "/portal/login":
            n = int(self.headers.get("Content-Length", 0))
            d = parse_qs(self.rfile.read(n).decode())
            user = d.get("user", [""])[0]; pw = d.get("pass", [""])[0]
            sql = f"SELECT user, rol FROM users WHERE user='{user}' AND pass='{pw}'"  # SQLi
            try: row = DB.execute(sql).fetchone()
            except Exception as e: return self._s(200, f"Error SQL: {e}", "text/plain")
            if row and row[1] == "admin":
                self._s(200, f"Bienvenido admin. Dashboard RRHH.\n{FLAG_FOOT}\n"
                             f"Backup de config disponible en: /backup/rrhh.conf\n", "text/plain")
            else:
                self._s(401, "Credenciales invalidas", "text/plain")
        else:
            self._s(404, "Not Found")

if __name__ == "__main__":
    print("[phantomcorp-clientes] engagement final arriba en :80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
