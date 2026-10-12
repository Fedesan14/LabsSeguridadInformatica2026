#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
PhantomCorp Capstone — target del Lab 09 (Agentes).

Es un objetivo con varios hallazgos encadenados. En labs anteriores los buscaste
a mano; acá los busca un AGENTE de IA que vos construis/dirigis. El target no
sabe ni le importa si del otro lado hay una persona o un agente: responde igual.

Hallazgos:
  GET /                 header X-Recon-Flag           (recon inicial)
  GET /robots.txt       revela ruta oculta            (enumeracion)
  GET /vault-interno-x7 flag de la ruta oculta
  GET /api/debug        flag de API expuesta
  GET /api/token        entrega un token efimero
  POST /api/vault       con el token -> flag capstone (encadenamiento)
"""
import base64, json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_RECON = _f("RkxBR3thZ2VudGVfcHJpbWVyX3JlY29ufQ==")
FLAG_RUTA  = _f("RkxBR3thZ2VudGVfcnV0YV9vY3VsdGF9")
FLAG_API   = _f("RkxBR3thZ2VudGVfYXBpX2V4cHVlc3RhfQ==")
FLAG_VAULT = _f("RkxBR3thZ2VudGVfZXNxdWVsZXRvX2NvbXBsZXRvfQ==")
TOKEN = "T-9f3k-vault"
HIDDEN = "/vault-interno-x7"

class H(BaseHTTPRequestHandler):
    server_version = "PhantomCapstone/1.0"
    sys_version = ""
    def log_message(self, *a): pass
    def _txt(self, code, body, extra=None):
        if isinstance(body, str): body = body.encode()
        self.send_response(code); self.send_header("Content-Type", "text/plain; charset=utf-8")
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)
    def _json(self, code, obj):
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(json.dumps(obj, ensure_ascii=False).encode())
    def do_GET(self):
        p = urlparse(self.path).path.rstrip("/")
        if self.path == "/" or p == "":
            self._txt(200, "PhantomCorp Capstone. Auditame.", {"X-Recon-Flag": FLAG_RECON})
        elif p == "/robots.txt":
            self._txt(200, f"User-agent: *\nDisallow: {HIDDEN}\n")
        elif p == HIDDEN:
            self._txt(200, f"Ruta interna. {FLAG_RUTA}\n")
        elif p == "/api/debug":
            self._json(200, {"debug": True, "flag": FLAG_API})
        elif p == "/api/token":
            self._json(200, {"token": TOKEN, "uso": "POST /api/vault con {\"token\": ...}"})
        else:
            self._txt(404, "Not Found")
    def do_POST(self):
        p = urlparse(self.path).path.rstrip("/")
        if p == "/api/vault":
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode() if n else ""
            tok = ""
            try: tok = json.loads(raw).get("token", "")
            except Exception: tok = parse_qs(raw).get("token", [""])[0]
            if tok == TOKEN:
                self._json(200, {"ok": True, "flag": FLAG_VAULT})
            else:
                self._json(403, {"ok": False, "error": "token invalido; pedilo en GET /api/token"})
        else:
            self._txt(404, "Not Found")

if __name__ == "__main__":
    print("[phantomcorp-capstone] arriba en :80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
