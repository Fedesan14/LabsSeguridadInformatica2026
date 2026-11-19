#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
objetivo/server.py — portal de empleados PhantomCorp con JWT, Lab Extra 5.

La app firma JWT con HMAC-SHA256. Los problemas, a propósito:

  R1  El payload del token trae un claim interno que no debería viajar
      (el JWT NO está cifrado: es solo base64url — cualquiera lo lee).
  R2  El secreto de firma es DÉBIL (está en cualquier diccionario chico).
      Quien lo crackea firma sus propios tokens: role=admin -> /admin.
  R3  La identidad es solo un claim: con el secreto, sub=maria te convierte
      en maria. Sus datos personales viajan en /perfil.

Corré:  python3 server.py        (o PORT=xxxx python3 server.py)
"""
import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def _f(b64: str) -> str:
    return base64.b64decode(b64).decode()


# El secreto es débil A PROPÓSITO (R2). Se descubre crackeando la firma,
# no leyendo esto.
SECRETO = _f("bWF0ZTEyMw==").encode()          # está en diccionario.txt
FLAG_CLAIM = _f("RkxBR3tqd3Rfc29sb19iYXNlNjR9")            # R1
FLAG_ADMIN = _f("RkxBR3tqd3RfZm9yamFkb19hZG1pbn0=")        # R2
FLAG_MARIA = _f("RkxBR3tqd3Rfc3VwbGFudGFjaW9uX2lkb3J9")    # R3

USUARIOS = {  # demo pública del portal (las credenciales están en la home)
    "diego": {"pass": "diego123", "role": "user",
              "datos": "Legajo 1042 — Soporte técnico"},
    "maria": {"pass": "maria456", "role": "user",
              "datos": f"Legajo 1007 — Finanzas. Nota confidencial: {FLAG_MARIA}"},
}


def b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def b64url_dec(texto: str) -> bytes:
    pad = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode(texto + pad)


def firmar(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    partes = b64url(json.dumps(header, separators=(",", ":")).encode()) + "." \
           + b64url(json.dumps(payload, separators=(",", ":")).encode())
    firma = hmac.new(SECRETO, partes.encode(), hashlib.sha256).digest()
    return partes + "." + b64url(firma)


def verificar(token: str):
    """Devuelve el payload si la firma es válida y no expiró; None si no."""
    try:
        cab, pay, fir = token.split(".")
        esperada = b64url(hmac.new(SECRETO, f"{cab}.{pay}".encode(),
                                   hashlib.sha256).digest())
        if not hmac.compare_digest(fir, esperada):
            return None
        payload = json.loads(b64url_dec(pay))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


HOME = """<!doctype html><html><body style="font-family:sans-serif;max-width:720px;margin:3em auto">
<h1>PhantomCorp — Portal de empleados</h1>
<p>Demo pública: <code>diego / diego123</code> o <code>maria / maria456</code>.</p>
<p><code>GET /login?user=diego&pass=diego123</code> devuelve tu token JWT.<br>
Usalo con <code>Authorization: Bearer &lt;token&gt;</code> en <code>/perfil</code>.<br>
El área de administración (<code>/admin</code>) es solo para role=admin.</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, qs = self.path.partition("?")
        params = parse_qs(qs)

        if path == "/":
            self._send(200, HOME.encode(), "text/html")
        elif path == "/login":
            user = params.get("user", [""])[0]
            pwd = params.get("pass", [""])[0]
            u = USUARIOS.get(user)
            if not u or u["pass"] != pwd:
                self._send(401, b'{"error": "credenciales invalidas"}',
                           "application/json")
                return
            payload = {
                "sub": user, "role": u["role"],
                "iat": int(time.time()), "exp": int(time.time()) + 3600,
                # R1: esto NO debería viajar en el token (no está cifrado!)
                "nota_interna": f"deploy-tag {FLAG_CLAIM}",
            }
            self._send(200, json.dumps({"token": firmar(payload)}).encode(),
                       "application/json")
        elif path == "/perfil":
            payload = self._payload_o_401()
            if not payload:
                return
            u = USUARIOS.get(payload["sub"])
            if not u:
                self._send(404, b'{"error": "usuario inexistente"}',
                           "application/json")
                return
            self._send(200, json.dumps({"usuario": payload["sub"],
                                        "role": u["role"],
                                        "datos": u["datos"]}).encode(),
                       "application/json")
        elif path == "/admin":
            payload = self._payload_o_401()
            if not payload:
                return
            if payload.get("role") != "admin":
                self._send(403, b'{"error": "solo administradores"}',
                           "application/json")
                return
            # R2: corona del lab
            self._send(200, json.dumps({"panel": "admin",
                                        "auditoria": FLAG_ADMIN}).encode(),
                       "application/json")
        else:
            self._send(404, b"404", "text/plain")

    def _payload_o_401(self):
        auth = self.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()
        payload = verificar(token) if token else None
        if not payload:
            self._send(401, b'{"error": "token invalido o expirado"}',
                       "application/json")
            return None
        return payload

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", "8080"))
    print(f"Portal PhantomCorp (JWT) en 0.0.0.0:{puerto}")
    ThreadingHTTPServer(("0.0.0.0", puerto), Handler).serve_forever()
