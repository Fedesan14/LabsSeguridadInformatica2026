#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
phantomcorp-db — host INTERNO del Lab 08.

No es alcanzable desde la consola del atacante: vive en una red segmentada a la
que solo llega el host comprometido. Para tocarlo hay que PIVOTEAR desde la
victima. Sirve:
    /              -> confirma que pivoteaste (flag R4)
    /empleado?id=N -> un legajo por id (1..250). UN solo id esconde el flag R5;
                      encontrarlo a mano es inviable: hay que AUTOMATIZAR.
"""
import base64, json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b): return base64.b64decode(b).decode()
FLAG_PIVOT = _f("RkxBR3twaXZvdF9pbnRlcm5hbF9ob3N0fQ==")
FLAG_AUTO  = _f("RkxBR3thdXRvbWF0aW9uX3BheXNfb2ZmfQ==")
MAGIC_ID = 187   # el unico legajo con el flag

class H(BaseHTTPRequestHandler):
    server_version = "PhantomDB-API/1.0"
    sys_version = ""
    def log_message(self, *a): pass
    def _json(self, code, obj):
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(json.dumps(obj, ensure_ascii=False).encode())
    def do_GET(self):
        u = urlparse(self.path); path = u.path.rstrip("/")
        if u.path == "/" or path == "":
            self._json(200, {"host": "phantomcorp-db", "msg": "Base de datos interna. Acceso restringido a la LAN.",
                             "pivot": FLAG_PIVOT})
        elif path == "/empleado":
            try: pid = int(parse_qs(u.query).get("id", ["0"])[0])
            except ValueError: pid = 0
            if pid == MAGIC_ID:
                self._json(200, {"id": pid, "nombre": "cuenta-servicio", "legajo_oculto": FLAG_AUTO})
            elif 1 <= pid <= 250:
                self._json(200, {"id": pid, "nombre": f"empleado_{pid}", "area": "operaciones"})
            else:
                self._json(404, {"error": "legajo inexistente"})
        else:
            self._json(404, {"error": "not found"})

if __name__ == "__main__":
    print("[phantomcorp-db] host interno arriba en :80", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 80), H).serve_forever()
