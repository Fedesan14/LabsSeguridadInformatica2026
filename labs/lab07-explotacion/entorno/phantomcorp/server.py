#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp Portal — target del Lab 07 (Explotación).

Enumeraste (lab 06). Ahora EXPLOTÁS: convertís los hallazgos en acceso. Esta app
tiene backend sqlite REAL, así que la inyección SQL es auténtica (podrías incluso
correr sqlmap). Cinco vulnerabilidades explotables, cada una con su flag.

    R1  SQLi bypass de autenticacion   POST /login
    R2  SQLi extraccion con UNION       GET  /buscar?q=
    R3  Inyeccion de comandos           GET  /herramientas/ping?host=
    R4  Path traversal (LFI)            GET  /descargar?archivo=
    R5  IDOR (control de acceso roto)   GET  /perfil?id=

Vulnerable A PROPOSITO. Solo se opera dentro del lab. Flags ofuscadas en base64.
"""
import base64, os, sqlite3, json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_AUTH  = _f("RkxBR3tzcWxpX2F1dGhfYnlwYXNzfQ==")
FLAG_UNION = _f("RkxBR3tzcWxpX3VuaW9uX2R1bXB9")
FLAG_CMDI  = _f("RkxBR3tjb21tYW5kX2luamVjdGlvbl9yY2V9")
FLAG_LFI   = _f("RkxBR3twYXRoX3RyYXZlcnNhbF9sZml9")
FLAG_IDOR  = _f("RkxBR3tpZG9yX2Jyb2tlbl9hY2Nlc3N9")

# --- Preparar el "sistema de archivos" para LFI y command injection ---
os.chdir("/app")
os.makedirs("/app/flags", exist_ok=True)
os.makedirs("/app/public", exist_ok=True)
open("/app/flags/lfi.txt", "w").write(FLAG_LFI + "\n")
open("/app/flags/cmdi.txt", "w").write(FLAG_CMDI + "\n")
open("/app/public/catalogo.txt", "w").write("Catalogo publico PhantomCorp.\n")

# --- Base de datos sqlite (en memoria, real) ---
def build_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    c = db.cursor()
    c.execute("CREATE TABLE users(id INTEGER, user TEXT, pass TEXT, rol TEXT, nota_privada TEXT)")
    c.executemany("INSERT INTO users VALUES(?,?,?,?,?)", [
        (1, "admin",  "s3cr3t-no-lo-vas-a-adivinar", "admin",
            f"Nota del admin: {FLAG_IDOR}"),
        (3, "jperez", "jperez123", "user", "Nota de Juan: acordarse de renovar cert."),
        (4, "mgomez", "verano2024", "user", "Nota de Maria: pedir vacaciones."),
    ])
    c.execute("CREATE TABLE productos(nombre TEXT, precio TEXT)")
    c.executemany("INSERT INTO productos VALUES(?,?)", [
        ("Router industrial", "1200"), ("Switch 48p", "800"), ("Firewall", "3400")])
    c.execute("CREATE TABLE secrets(clave TEXT, valor TEXT)")
    c.execute("INSERT INTO secrets VALUES(?,?)", ("flag_union", FLAG_UNION))
    db.commit()
    return db
DB = build_db()

class H(BaseHTTPRequestHandler):
    server_version = "PhantomPortal/1.0"
    sys_version = ""
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        if isinstance(body, str): body = body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query); path = u.path.rstrip("/")
        if u.path == "/" or path == "":
            self._send(200, "Portal PhantomCorp. Endpoints: /login /buscar /herramientas/ping /descargar /perfil")
        elif path == "/buscar":
            termino = (q.get("q", [""])[0])
            # VULN R2: consulta concatenada -> UNION injection
            sql = f"SELECT nombre, precio FROM productos WHERE nombre LIKE '%{termino}%'"
            try:
                filas = DB.execute(sql).fetchall()
                self._send(200, "Resultados:\n" + "\n".join(f"  {n} - ${p}" for n, p in filas))
            except Exception as e:
                self._send(200, f"Error SQL: {e}")   # el error ayuda a inyectar (verboso a propósito)
        elif path == "/herramientas/ping":
            host = q.get("host", ["127.0.0.1"])[0]
            # VULN R3: command injection
            salida = os.popen(f"ping -c1 {host} 2>&1").read()
            self._send(200, f"$ ping -c1 {host}\n{salida}")
        elif path == "/descargar":
            archivo = q.get("archivo", ["catalogo.txt"])[0]
            # VULN R4: path traversal (sin sanitizar)
            try:
                with open(f"/app/public/{archivo}", "r") as fh:
                    self._send(200, fh.read())
            except Exception as e:
                self._send(404, f"No se pudo abrir: {e}")
        elif path == "/perfil":
            pid = q.get("id", ["3"])[0]
            # VULN R5: IDOR - no valida que el perfil sea tuyo
            fila = DB.execute("SELECT id,user,rol,nota_privada FROM users WHERE id=?", (pid,)).fetchone()
            if fila:
                self._send(200, json.dumps({"id": fila[0], "user": fila[1], "rol": fila[2],
                                            "nota_privada": fila[3]}, ensure_ascii=False),
                           "application/json")
            else:
                self._send(404, "Perfil inexistente")
        else:
            self._send(404, "Not Found")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path.rstrip("/") == "/login":
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n).decode()
            p = parse_qs(body)
            user = p.get("user", [""])[0]; pw = p.get("pass", [""])[0]
            # VULN R1: query concatenada -> bypass de autenticacion
            sql = f"SELECT user, rol FROM users WHERE user='{user}' AND pass='{pw}'"
            try:
                fila = DB.execute(sql).fetchone()
            except Exception as e:
                self._send(200, f"Error SQL: {e}"); return
            if fila:
                msg = f"Bienvenido {fila[0]} (rol: {fila[1]}).\n"
                if fila[1] == "admin":
                    msg += f"Panel de administracion desbloqueado: {FLAG_AUTH}\n"
                self._send(200, msg)
            else:
                self._send(401, "Credenciales invalidas")
        else:
            self._send(404, "Not Found")

if __name__ == "__main__":
    print("[phantomcorp-portal] arriba en :80 (sqlite real, vulnerable)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
