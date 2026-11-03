#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
objetivo/server.py — PhantomCorp, copia PARCHADA del Grupo 03 (Lab Extra 3).

Las cinco defensas D1-D5 originales del objetivo "roto" quedaron resueltas acá
con fixes estructurales (no cosméticos). Ver informe.md para el detalle de
cada una (antes/después, diff, verificación).
"""
import base64
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB = "/tmp/phantom_hardening.db"
DESCARGAS = "/tmp/phantom_descargas"    # raíz "pública" de /descargar
# D5: directorio real y normalizado una sola vez, para confinar por PATH
# RESUELTO (no por substrings del nombre pedido, que se pueden ofuscar).
DESCARGAS_REAL = os.path.realpath(DESCARGAS)


def init_db():
    if os.path.exists(DB):
        os.remove(DB)
    db = sqlite3.connect(DB)
    db.execute("CREATE TABLE usuarios (user TEXT, password TEXT)")
    db.execute("INSERT INTO usuarios VALUES ('admin', 'sup3r-s3cr3t0')")
    db.commit()
    db.close()
    os.makedirs(DESCARGAS, exist_ok=True)
    with open(os.path.join(DESCARGAS, "manual.txt"), "w") as fh:
        fh.write("Manual de la intranet PhantomCorp.\n")


class Handler(BaseHTTPRequestHandler):
    # D1: no seteamos server_version/sys_version con producto+versión, y
    # además pisamos version_string() más abajo para que el header Server
    # no exista en absoluto (no solo "menos informativo": ausente).
    server_version = ""
    sys_version = ""

    def version_string(self):
        # D1: sin esto, BaseHTTPRequestHandler arma igual un header Server
        # con server_version+sys_version. Lo neutralizamos en la fuente.
        return ""

    def send_response(self, code, message=None):
        # D1: send_response() de la clase base agrega SIEMPRE un header
        # Server con version_string(). Lo reescribimos para no emitirlo
        # (no "vaciarlo": sacarlo del todo es el fix real, no cosmético).
        # Mantenemos log_request() igual que la clase base: no es parte
        # del fix, y log_message() ya es un no-op en esta clase.
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header("Date", self.date_time_string())

    def do_GET(self):
        path, _, qs = self.path.partition("?")
        params = parse_qs(qs)

        if path == "/":
            self._html(200, "<h1>PhantomCorp</h1><p>Portal de empleados.</p>")
        elif path == "/robots.txt":
            # D3: ya no hay rutas sensibles que listar (se eliminaron abajo).
            self._txt(200, "User-agent: *\n")
        elif path == "/login":
            # D4: consulta PARAMETRIZADA. El motor separa código de datos:
            # lo que venga en user/pwd nunca se interpreta como SQL, sea lo
            # que sea que contenga (comillas, --, OR 1=1, etc).
            user = params.get("user", [""])[0]
            pwd = params.get("pass", [""])[0]
            db = sqlite3.connect(DB)
            cur = db.execute(
                "SELECT user FROM usuarios WHERE user = ? AND password = ?",
                (user, pwd),
            )
            if cur.fetchone():
                self._html(200, "<h1>Bienvenido, " + user + "</h1>")
            else:
                self._html(401, "<h1>Credenciales inválidas</h1>")
            db.close()
        elif path == "/descargar":
            # D5: confinamos por PATH RESUELTO, no por filtrar el string
            # pedido. Cualquier forma de escribir ".." (literal, %2e%2e%2f
            # ya decodeado por parse_qs, "....//", absoluto, symlink) termina
            # en un path real; si ese path real no cae DENTRO de
            # DESCARGAS_REAL, se rechaza, sin importar cómo se escribió.
            nombre = params.get("archivo", [""])[0]
            destino = os.path.realpath(os.path.join(DESCARGAS, nombre))
            dentro = (
                destino == DESCARGAS_REAL
                or destino.startswith(DESCARGAS_REAL + os.sep)
            )
            if not dentro:
                self._txt(404, "no encontrado")
                return
            try:
                with open(destino, "rb") as fh:
                    self._txt(200, fh.read(8192).decode("utf-8", "ignore"))
            except Exception:
                self._txt(404, "no encontrado")
        else:
            # D2 y D3 (parte "/backup"): esos endpoints de debug/backup NO
            # EXISTEN más. No es "ocultarlos": se borraron del código, así
            # que caen acá como cualquier ruta inexistente.
            self._txt(404, "404 - no existe")

    # --- helpers de respuesta ---
    def _html(self, code, body):
        self._send(code, body.encode(), "text/html; charset=utf-8")

    def _txt(self, code, body):
        self._send(code, body.encode(), "text/plain; charset=utf-8")

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    init_db()
    puerto = int(os.environ.get("PORT", "8080"))
    print(f"PhantomCorp (endurecido — Grupo 03) en 0.0.0.0:{puerto}")
    ThreadingHTTPServer(("0.0.0.0", puerto), Handler).serve_forever()
