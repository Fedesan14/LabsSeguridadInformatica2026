# Intranet de PhantomCorp — SOLO existe en la red interna (internalnet).
# La consola atacante NO la alcanza directamente: hay que pedirle al servidor
# público que la fetchee (SSRF).
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def _f(b64: str) -> str:
    return base64.b64decode(b64).decode()

FLAG_INTRANET = _f("RkxBR3tzc3JmX2ludHJhbmV0X2Rlc2N1YmllcnRhfQ==")  # R2
FLAG_BACKUP   = _f("RkxBR3tzc3JmX2JhY2t1cF9jbGllbnRlc30=")          # R3

HOME = f"""<!doctype html><html><body style="font-family:sans-serif">
<h1>Intranet PhantomCorp</h1>
<p><b>USO INTERNO.</b> Si la estás viendo desde afuera, avisá a Seguridad.</p>
<p>Host: <b>{FLAG_INTRANET}</b></p>
<ul>
  <li><a href="/backups/clientes.json">backup de clientes (temporal, borrar!)</a></li>
  <li><a href="/salud">estado del servicio</a></li>
</ul>
</body></html>"""

BACKUP = """{
  "_aviso": "backup temporal pre-migracion. NO deberia ser accesible.",
  "clientes": [
    {"id": 1, "empresa": "Aconcagua SRL", "cuit": "30-70998877-1"},
    {"id": 2, "empresa": "Comechingones SA", "cuit": "30-71554433-6"}
  ],
  "integridad": "%s"
}""" % FLAG_BACKUP

SALUD = '{"estado": "ok", "servicio": "intranet-phantomcorp"}'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._send(200, HOME.encode(), "text/html")
        elif self.path == "/backups/clientes.json":
            self._send(200, BACKUP.encode(), "application/json")
        elif self.path == "/salud":
            self._send(200, SALUD.encode(), "application/json")
        else:
            self._send(404, b"404", "text/plain")

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import os
    puerto = int(os.environ.get("PORT", "80"))
    print(f"intranet en 0.0.0.0:{puerto} (solo internalnet)")
    ThreadingHTTPServer(("0.0.0.0", puerto), Handler).serve_forever()
