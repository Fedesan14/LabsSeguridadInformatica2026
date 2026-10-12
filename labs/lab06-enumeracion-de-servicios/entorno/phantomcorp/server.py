#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp Intranet — target del Lab 06 (Enumeración).

El recon (lab 05) te dio el MAPA: sabés qué puertos y servicios hay. Enumerar es
el paso siguiente: meterte en cada servicio y sacarle TODO — rutas, archivos,
usuarios, versiones, métodos habilitados. Este target es una intranet web con
cinco cosas mal configuradas, cada una descubrible con una técnica de enum
distinta. Flags ofuscadas en base64: se ganan enumerando, no leyendo esto.
"""
import base64, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_DIR   = _f("RkxBR3tkaXJfZW51bWVyYXRpb25fYmFja3VwfQ==")
FLAG_GIT   = _f("RkxBR3tnaXRfcmVwb19leHBvc2VkfQ==")
FLAG_HTTP  = _f("RkxBR3todHRwX21ldGhvZHNfcHV0X2VuYWJsZWR9")
FLAG_USERS = _f("RkxBR3t1c2VyX2VudW1lcmF0aW9uX2FwaX0=")
FLAG_TECH  = _f("RkxBR3t0ZWNoX2ZpbmdlcnByaW50X3BoYW50b21jbXN9")

INDEX = b"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="generator" content="PhantomCMS 3.7">
<title>Intranet PhantomCorp</title></head><body>
<h1>Intranet PhantomCorp S.A.</h1>
<p>Acceso solo para personal. Portal interno v3.7.</p>
</body></html>"""

# rutas descubribles por fuerza bruta de directorios (dirb/gobuster)
BACKUP = f"""<!doctype html><html><body><h1>Index of /backup</h1>
<pre>
respaldo-db-2024.sql.gz
config.old
notas-infra.txt   ->  {FLAG_DIR}
</pre>
<p>Este directorio no deberia estar accesible. Enumeracion de directorios 101.</p>
</body></html>""".encode()

GIT_CONFIG = f"""[core]
\trepositoryformatversion = 0
\tbare = false
[remote "origin"]
\turl = https://git.internal.phantomcorp/intranet.git
# Un .git expuesto filtra codigo, historia y a veces secretos.
# {FLAG_GIT}
""".encode()

USERS = json.dumps({
    "users": [
        {"id": 1, "user": "admin",   "role": "superuser"},
        {"id": 2, "user": "jperez",  "role": "editor"},
        {"id": 3, "user": "mgomez",  "role": "viewer"},
    ],
    "note": "endpoint interno de RRHH - no exponer",
    "flag": FLAG_USERS,
}).encode()

VERSION = (f"PhantomCMS 3.7 (build 2024-11)\n"
           f"Archivo default del CMS. Si llegaste aca por fingerprinting, bien.\n"
           f"{FLAG_TECH}\n").encode()

class H(BaseHTTPRequestHandler):
    server_version = "PhantomServer/3.7"
    sys_version = ""
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Powered-By", "PhantomCMS/3.7")  # pista de fingerprint
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self):
        # Metodos peligrosos habilitados: PUT/DELETE en produccion = problema.
        self.send_response(200)
        self.send_header("Allow", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("X-Dangerous-Methods", FLAG_HTTP)
        self.end_headers()
    def do_GET(self):
        p = self.path.rstrip("/")
        if p == "" or self.path == "/":            self._send(200, INDEX)
        elif p == "/backup":                        self._send(200, BACKUP)
        elif p == "/.git/config":                   self._send(200, GIT_CONFIG, "text/plain; charset=utf-8")
        elif p == "/api/users":                     self._send(200, USERS, "application/json")
        elif p == "/phantomcms/VERSION":            self._send(200, VERSION, "text/plain; charset=utf-8")
        elif p == "/admin":                         self._send(403, b"<h1>403 Forbidden</h1><p>Panel admin. Necesitas credenciales.</p>")
        else:                                       self._send(404, b"<h1>404 Not Found</h1>")

if __name__ == "__main__":
    print("[phantomcorp-intranet] arriba en :80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
