#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp — target deliberadamente vulnerable del Lab 05 (Reconocimiento).

Levanta CUATRO servicios en un solo contenedor para que el alumno los descubra
con nmap y los interrogue con las tools. NO hay nada que "hackear" acá: el
objetivo del lab es RECONOCER y CLASIFICAR lo que está expuesto.

    21    /tcp   Banner FTP (versión vieja, para clasificar contra CVEs)
    80    /tcp   Web corporativa (headers que filtran info + robots.txt)
    8080  /tcp   Servicio "dev" olvidado en producción (endpoint /status)
    31337 /tcp   Servicio de mantenimiento en puerto alto no estándar

Cada servicio esconde una FLAG. Se descubren HACIENDO recon, no leyendo esto:
por eso van ofuscadas en base64. Igual, si estás leyendo el código del target
en vez de escanearlo... ojo, eso también es una técnica de recon. Pero hacé el
lab con las tools primero, loco. Se aprende haciendo.
"""
import base64
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b64: str) -> str:
    return base64.b64decode(b64).decode()

FLAG_HIGHPORT = _f("RkxBR3toaWdoX3BvcnRfc2VjcmV0X3NlcnZpY2V9")
FLAG_FTP      = _f("RkxBR3tiYW5uZXJfZ3JhYl9wcm9mdHBkXzEzNX0=")
FLAG_HTTPHDR  = _f("RkxBR3todHRwX2hlYWRlcnNfbGVha19pbmZvfQ==")
FLAG_HIDDEN   = _f("RkxBR3tyZWNvbl9oaWRkZW5fcGF0aH0=")
FLAG_DEV      = _f("RkxBR3tkZXZfc2VydmljZV9leHBvc2VkfQ==")

HIDDEN_PATH = "/panel-interno-9x2f"

# ── Puerto 80: web corporativa ──────────────────────────────────────────────
INDEX = b"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>PhantomCorp S.A. - Soluciones Logisticas</title></head><body>
<h1>PhantomCorp S.A.</h1>
<p>Lideres en logistica desde 1998. Portal corporativo.</p>
<!-- TODO(infra): sacar el panel interno de produccion antes del go-live -->
</body></html>"""

ROBOTS = f"""User-agent: *
Disallow: /admin
Disallow: {HIDDEN_PATH}
# Recordatorio infra: {HIDDEN_PATH} sigue accesible desde afuera. Migrar a VPN.
""".encode()

HIDDEN_PAGE = f"""<!doctype html><html><body>
<h1>Panel interno PhantomCorp</h1>
<p>Acceso restringido. Si llegaste aca por robots.txt, felicitaciones: acabas
de hacer enumeracion de rutas. Esa es exactamente la tecnica.</p>
<pre>{FLAG_HIDDEN}</pre>
</body></html>""".encode()

class WebHandler(BaseHTTPRequestHandler):
    server_version = "PhantomServer/2.4.1"     # banner que se filtra en headers
    sys_version = ""                            # ocultamos "Python/x.y" a propósito
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Powered-By", "PhantomCMS 2.4.1")
        self.send_header("X-Backend-Flag", FLAG_HTTPHDR)   # header custom = info leak
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
    def do_HEAD(self):
        # curl -I manda HEAD: respondemos headers (con el leak) pero sin cuerpo.
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Powered-By", "PhantomCMS 2.4.1")
        self.send_header("X-Backend-Flag", FLAG_HTTPHDR)
        self.end_headers()
    def do_GET(self):
        if self.path == "/robots.txt":
            self._send(200, ROBOTS, "text/plain; charset=utf-8")
        elif self.path.rstrip("/") == HIDDEN_PATH:
            self._send(200, HIDDEN_PAGE)
        elif self.path == "/":
            self._send(200, INDEX)
        else:
            self._send(404, b"<h1>404</h1>")

# ── Puerto 8080: servicio dev olvidado ──────────────────────────────────────
class DevHandler(BaseHTTPRequestHandler):
    server_version = "Werkzeug/2.0.1"          # versión concreta para clasificar
    sys_version = "Python/3.9.2"
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/status":
            body = (b'{"service":"phantom-dev-api","version":"0.9.3-DEV",'
                    b'"debug":true,"flag":"' + FLAG_DEV.encode() + b'"}')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"phantom-dev-api. Proba /status")

# ── Puertos crudos 21 y 31337: banners por socket ───────────────────────────
def banner_server(port, banner: bytes):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port)); s.listen(16)
    while True:
        conn, _ = s.accept()
        try:
            conn.sendall(banner)
        except OSError:
            pass
        finally:
            conn.close()

def serve_http(port, handler):
    ThreadingHTTPServer(("0.0.0.0", port), handler).serve_forever()

if __name__ == "__main__":
    ftp_banner = (f"220 ProFTPD 1.3.5 Server (PhantomCorp FTP) [::ffff:0.0.0.0]\r\n"
                  f"214 {FLAG_FTP}\r\n").encode()
    maint_banner = ("PhantomCorp maintenance shell v0.1 -- acceso no autorizado prohibido\n"
                    f"{FLAG_HIGHPORT}\n").encode()
    threading.Thread(target=banner_server, args=(21, ftp_banner), daemon=True).start()
    threading.Thread(target=banner_server, args=(31337, maint_banner), daemon=True).start()
    threading.Thread(target=serve_http, args=(8080, DevHandler), daemon=True).start()
    print("[phantomcorp] servicios arriba en 21, 80, 8080, 31337", flush=True)
    serve_http(80, WebHandler)   # bloquea el hilo principal
