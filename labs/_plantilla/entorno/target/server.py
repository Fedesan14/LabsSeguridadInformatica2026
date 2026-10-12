#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""Target placeholder del lab NN. Reemplazá por el tuyo.
Esconde las flags en el comportamiento (banner/header/respuesta), ofuscadas."""
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLAG = base64.b64decode("RkxBR3twbGFudGlsbGF9").decode()  # FLAG{plantilla}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"target placeholder — reemplazame. {FLAG}\n".encode())

if __name__ == "__main__":
    print("[target] arriba en :80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
