"""Panel web local del swarm: lo mismo que la CLI, pero en el navegador.

Sólo biblioteca estándar. Escucha únicamente en 127.0.0.1. Como cualquier
página abierta en el navegador puede mandarle pedidos a localhost, hay dos
controles en la frontera:

- El header Host tiene que ser 127.0.0.1 o localhost: frena el DNS rebinding,
  donde un dominio ajeno pasa a resolver a 127.0.0.1.
- Cada pedido a /api/ lleva un token que sólo conoce la página servida acá:
  frena el CSRF, porque otra página no puede leer ese token.

El target no se elige en el panel: es `roe.OBJETIVO`, igual que en la CLI, y
toda acción sigue pasando por `roe.validar` dentro del orquestador.
"""
import hmac
import json
import os
import pathlib
import re
import secrets
import subprocess
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from agentes import AgenteEnum, AgentePicaro, AgenteRecon, hallazgos_http
from bitacora import Bitacora, verificar
from orquestador import correr
from roe import OBJETIVO
from sandbox import RED, ejecutar_docker

AQUI = pathlib.Path(__file__).resolve().parent
# entregas/labfinal/grupo03/ptaas -> raíz del repo, donde vive .loot/ (gitignored).
LOOT = AQUI.parents[3] / ".loot"
PUERTO = 8765
TOKEN = secrets.token_urlsafe(24)
NOMBRE = re.compile(r"^[\w.-]{1,80}\.jsonl$")
MAX_CUERPO = 10_000

estado = {"corriendo": False, "archivo": None, "error": None, "hallazgos": None, "cabeza": None}
candado = threading.Lock()


def ruta_bitacora(nombre) -> pathlib.Path:
    """El nombre viene del navegador: sólo se acepta un archivo .jsonl dentro de .loot/."""
    if not isinstance(nombre, str) or not NOMBRE.fullmatch(nombre):
        raise ValueError("nombre de bitácora inválido: sólo letras, números, . - _ y terminado en .jsonl")
    ruta = (LOOT / nombre).resolve()
    if ruta.parent != LOOT.resolve():
        raise ValueError("la bitácora tiene que estar dentro de .loot/")
    return ruta


def clave_de(datos) -> bytes:
    clave = datos.get("clave")
    if not isinstance(clave, str) or not clave:
        raise ValueError("falta la clave HMAC")
    return clave.encode("utf-8")


def leer_eventos(ruta):
    eventos = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            eventos.append(json.loads(linea))
        except ValueError:
            # Durante una corrida, la última línea puede estar a medio escribir.
            break
    return eventos


def chequear_docker():
    try:
        if subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode != 0:
            return "Docker no está corriendo: abrí Docker Desktop y esperá a que diga Engine running."
        if subprocess.run(["docker", "network", "inspect", RED], capture_output=True, timeout=30).returncode != 0:
            return f"No existe la red {RED}: levantá el lab final (paso 14 de PRUEBAS.md)."
    except (OSError, subprocess.TimeoutExpired):
        return "No se encontró el comando docker: instalá Docker Desktop."
    return None


def _corrida(bitacora):
    try:
        pizarra = correr([AgenteRecon(), AgenteEnum()], bitacora, ejecutar_docker)
        estado["hallazgos"] = {
            "puertos": pizarra.get("puertos", {}),
            "rutas": [{"puerto": p, "ruta": r, "codigo": c} for (p, r), c in sorted(hallazgos_http(pizarra).items())],
        }
        estado["cabeza"] = bitacora.ultimo
    except Exception as e:
        estado["error"] = f"la corrida se cortó: {e}"
    finally:
        estado["corriendo"] = False


def iniciar_corrida(datos):
    ruta_bitacora(datos.get("nombre"))
    clave_de(datos)
    with candado:
        if estado["corriendo"]:
            raise ValueError("ya hay una corrida en curso")
        problema = chequear_docker()
        if problema:
            raise ValueError(problema)
        bitacora = nueva_bitacora(datos)
        nombre = pathlib.Path(bitacora.ruta).name
        estado.update(corriendo=True, archivo=nombre, error=None, hallazgos=None, cabeza=None)
    threading.Thread(target=_corrida, args=(bitacora,), daemon=True).start()
    return {"archivo": nombre}


def nueva_bitacora(datos):
    ruta, clave = ruta_bitacora(datos.get("nombre")), clave_de(datos)
    LOOT.mkdir(exist_ok=True)
    try:
        return Bitacora(ruta, clave)
    except FileExistsError:
        raise ValueError(f"{ruta.name} ya existe: la bitácora nunca se pisa, elegí otro nombre") from None


def _sin_sandbox(argv):
    raise ValueError(f"la RoE dejó pasar una acción que tenía que rechazar: {argv}")


def probar_roe(datos):
    """Corre el agente pícaro con el orquestador real, sin Docker.

    No hace falta sandbox: todo lo que propone ese agente tiene que quedar
    rechazado por la RoE. Si algo llegara a ejecutarse, `_sin_sandbox` corta.
    """
    bitacora = nueva_bitacora(datos)
    correr([AgentePicaro()], bitacora, _sin_sandbox)
    return {"archivo": pathlib.Path(bitacora.ruta).name, "cabeza": bitacora.ultimo}


def verificar_bitacora(datos):
    ruta, clave = ruta_bitacora(datos.get("nombre")), clave_de(datos)
    try:
        return {"integra": True, "cabeza": verificar(ruta, clave)}
    except ValueError as e:
        return {"integra": False, "mensaje": str(e)}


def demo_alteracion(ruta, clave):
    """Altera un resultado en una copia temporal y muestra dónde se rompe la cadena.

    El original no se toca. Se elige un resultado del medio: alterar la última
    línea no rompe nada hacia atrás (eso se detecta contra la cabeza publicada).
    """
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    candidatas = [i for i, l in enumerate(lineas[:-1]) if json.loads(l)["evento"] == "resultado"]
    if not candidatas:
        raise ValueError("la bitácora no tiene un resultado antes de la última línea")
    i = candidatas[len(candidatas) // 2]
    evento = json.loads(lineas[i])
    antes = evento["datos"].get("salida")
    evento["datos"]["salida"] = "404" if antes == "200" else "200"
    lineas[i] = json.dumps(evento, sort_keys=True, ensure_ascii=False)
    with tempfile.TemporaryDirectory() as d:
        copia = pathlib.Path(d, "alterada.jsonl")
        with open(copia, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(l + "\n" for l in lineas))
        try:
            verificar(copia, clave)
            mensaje = None
        except ValueError as e:
            mensaje = str(e)
    return {"linea": i + 1, "antes": antes, "despues": evento["datos"]["salida"],
            "detectada": mensaje is not None, "mensaje": mensaje}


def alterar(datos):
    ruta, clave = ruta_bitacora(datos.get("nombre")), clave_de(datos)
    try:
        verificar(ruta, clave)
    except ValueError as e:
        raise ValueError(f"la bitácora original no verifica (¿clave equivocada?): {e}") from None
    return demo_alteracion(ruta, clave)


def correr_test(_):
    r = subprocess.run([sys.executable, str(AQUI / "test_ptaas.py")], capture_output=True, text=True,
                       encoding="utf-8", timeout=120, cwd=AQUI, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return {"paso": r.returncode == 0, "salida": (r.stdout + r.stderr).strip()}


def listar_bitacoras():
    if not LOOT.is_dir():
        return []
    return [{"nombre": p.name, "bytes": p.stat().st_size}
            for p in sorted(LOOT.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
            if NOMBRE.fullmatch(p.name)]


ACCIONES = {"/api/correr": iniciar_corrida, "/api/verificar": verificar_bitacora,
            "/api/alterar": alterar, "/api/test": correr_test, "/api/probar-roe": probar_roe}


class Panel(BaseHTTPRequestHandler):
    def _permitido(self, api):
        puerto = self.server.server_address[1]
        if self.headers.get("Host") not in {f"127.0.0.1:{puerto}", f"localhost:{puerto}"}:
            return False
        return not api or hmac.compare_digest(self.headers.get("X-Token", "").encode(), TOKEN.encode())

    def _enviar(self, codigo, cuerpo, tipo, extra=()):
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(datos)

    def _json(self, codigo, datos):
        self._enviar(codigo, json.dumps(datos, ensure_ascii=False), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        if not self._permitido(url.path.startswith("/api/")):
            return self._json(403, {"error": "prohibido"})
        try:
            if url.path == "/":
                nonce = secrets.token_urlsafe(16)
                html = (AQUI / "panel.html").read_text(encoding="utf-8")
                html = html.replace("{{TOKEN}}", TOKEN).replace("{{NONCE}}", nonce).replace("{{OBJETIVO}}", OBJETIVO)
                csp = (f"default-src 'none'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline'; "
                       "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
                return self._enviar(200, html, "text/html; charset=utf-8", [("Content-Security-Policy", csp)])
            if url.path == "/api/estado":
                return self._json(200, {**estado, "objetivo": OBJETIVO})
            if url.path == "/api/bitacoras":
                return self._json(200, listar_bitacoras())
            if url.path == "/api/bitacora":
                ruta = ruta_bitacora(parse_qs(url.query).get("nombre", [""])[0])
                return self._json(200, leer_eventos(ruta))
            return self._json(404, {"error": "no existe"})
        except (ValueError, OSError) as e:
            return self._json(400, {"error": str(e)})

    def do_POST(self):
        url = urlparse(self.path)
        if not self._permitido(True):
            return self._json(403, {"error": "prohibido"})
        accion = ACCIONES.get(url.path)
        if accion is None:
            return self._json(404, {"error": "no existe"})
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            if not 0 <= largo <= MAX_CUERPO:
                raise ValueError("pedido demasiado grande")
            datos = json.loads(self.rfile.read(largo) or b"{}")
            if not isinstance(datos, dict):
                raise ValueError("se esperaba un objeto JSON")
            return self._json(200, accion(datos))
        except (ValueError, OSError, subprocess.TimeoutExpired) as e:
            return self._json(400, {"error": str(e)})

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Panel)
    url = f"http://127.0.0.1:{PUERTO}/"
    print(f"Panel del swarm en {url}  (Ctrl+C para cerrarlo)")
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.shutdown()
