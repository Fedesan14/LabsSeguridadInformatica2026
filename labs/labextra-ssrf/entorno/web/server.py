# Servidor web público de PhantomCorp — Lab Extra SSRF.
# Expone /preview?url= : una "herramienta para empleados" que fetchea URLs
# DESDE EL SERVIDOR. Sin validación de destino. Eso es SSRF (CWE-918).
#
# Además corre un panel interno en 127.0.0.1:9000 (NO accesible desde afuera:
# solo se alcanza pidiéndoselo al propio server a través del SSRF).
import base64
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

def _f(b64: str) -> str:
    return base64.b64decode(b64).decode()

# Las flags se DESCUBREN explotando el SSRF, no leyendo esto.
FLAG_PANEL = _f("RkxBR3tzc3JmX2xvY2FsaG9zdF9wYW5lbF9pbnRlcm5vfQ==")  # R1

HOME = """<!doctype html><html><head><title>PhantomCorp — Portal</title></head>
<body style="font-family:sans-serif;max-width:720px;margin:3em auto">
<h1>PhantomCorp S.A.</h1>
<p>Portal público. Novedades, carreras y contacto.</p>
<hr>
<h2>Herramientas para empleados</h2>
<form action="/preview" method="get">
  <label>Previsualizar URL:&nbsp;
    <input name="url" size="48" placeholder="https://ejemplo.com"></label>
  <button type="submit">Ver</button>
</form>
<p style="color:#777"><small>La previsualización la genera el servidor,
así no navegás sitios raros desde tu máquina. — IT</small></p>
</body></html>"""


class PublicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path, _, qs = self.path.partition("?")
        if path == "/":
            self._send(200, HOME.encode())
        elif path == "/preview":
            url = parse_qs(qs).get("url", [""])[0]
            self._preview(url)
        else:
            self._send(404, b"404 - no existe")

    def _preview(self, url: str):
        if not url:
            self._send(400, b"Falta el parametro ?url=")
            return
        # VULNERABILIDAD (a propósito): el server fetchea CUALQUIER URL,
        # sin allowlist de hosts, sin bloquear IPs internas ni localhost.
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                cuerpo = r.read(65536)
            salida = (b"<h3>Previsualizacion de " + url.encode() + b"</h3><hr>"
                      + cuerpo)
            self._send(200, salida)
        except Exception as e:
            self._send(502, f"No pude traer {url}: {e}".encode())

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class PanelInternoHandler(BaseHTTPRequestHandler):
    """Panel de administración. SOLO escucha en localhost: en teoría nadie de
    afuera debería poder verlo... salvo que el propio server lo pida."""

    def do_GET(self):
        if self.path.startswith("/"):
            cuerpo = f"""<!doctype html><html><body style="font-family:monospace">
<h2>PhantomCorp — Panel interno (solo localhost)</h2>
<p>Si estás viendo esto desde afuera, algo salió mal.</p>
<p>Deploy key: <b>{FLAG_PANEL}</b></p>
</body></html>"""
            self._send(200, cuerpo.encode())
        self.connection.close()

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import os
    puerto_publico = int(os.environ.get("PORT_PUBLICO", "80"))
    puerto_panel = int(os.environ.get("PORT_PANEL", "9000"))
    panel = ThreadingHTTPServer(("127.0.0.1", puerto_panel), PanelInternoHandler)
    threading.Thread(target=panel.serve_forever, daemon=True).start()
    print(f"panel interno en 127.0.0.1:{puerto_panel}")
    print(f"portal público en 0.0.0.0:{puerto_publico}")
    ThreadingHTTPServer(("0.0.0.0", puerto_publico), PublicHandler).serve_forever()
