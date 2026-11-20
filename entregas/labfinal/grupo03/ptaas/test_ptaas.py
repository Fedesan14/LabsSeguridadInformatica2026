"""Test del swarm sin Docker ni red: el sandbox se reemplaza por un falso con salidas fijas.

Corre con `python3 test_ptaas.py`. Si hay `openssl` en el PATH, la cadena de
la bitácora se recalcula con él: es la verificación independiente de que cada
`prev` es de verdad HMAC-SHA256 de la línea anterior, y no sólo que el código
coincide consigo mismo.
"""
import http.client
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import threading
from http.server import ThreadingHTTPServer

import panel
from agentes import (AgenteEnum, AgenteFoothold, AgenteImpacto, AgenteLoot,
                     AgentePicaro, AgenteRecon, hallazgos_http)
from bitacora import Bitacora, verificar
from orquestador import correr
from roe import Accion, validar

CLAVE = b"clave-de-prueba"
NMAP = ("PORT   STATE SERVICE VERSION\n"
        "22/tcp open  ssh     OpenSSH 9.6\n"
        "80/tcp open  http?\n")


ROBOTS = "User-agent: *\nDisallow: /portal-rrhh\nDisallow: /x;rm -rf /\n"

# Cuerpos fijos del sandbox falso para R1–R4. Las FLAG{...} son de prueba, no las
# reales del target: el test comprueba que el agente extrae la flag que venga en la
# respuesta, no un valor concreto.
PORTAL = ("<!doctype html><title>Portal RRHH</title><h1>Portal interno RRHH</h1>"
          "<form method=post action=/portal/login><input name=user></form>"
          "<!-- recon: portal interno localizado. FLAG{demo_recon} -->")
FOOTHOLD = ("Bienvenido admin. Dashboard RRHH.\nFLAG{demo_foothold}\n"
            "Backup de config disponible en: /backup/rrhh.conf\n")
BACKUP = ("DB_USER=rrhh_app\nDB_PASS=Rh-2026\nAPI_TOKEN=phantom-api-7c1e\n"
          "# token en /api/reporte?token=...&cmd=... FLAG{demo_token}\n")
IMPACTO = ("$ cat /app/priv/clientes.db.txt\n"
           "clientes: 48210 registros (nombre, DNI, tarjeta). FLAG{demo_crown}\n")


def falso(llamadas):
    def ejecutar(argv):
        llamadas.append(argv)
        if argv[0] == "nmap":
            return 0, NMAP
        if "--data" in argv:            # curl_post: login con SQLi (R2)
            return 0, FOOTHOLD
        if "-G" in argv:                # curl_api: comando con token (R4)
            return 0, IMPACTO
        if "-w" in argv:                # curl: sólo el código HTTP (enum)
            return 0, "200" if argv[-1].endswith((":80/interno", ":80/portal-rrhh")) else "404"
        url = argv[-1]                  # curl_cuerpo: lee el cuerpo
        if url.endswith("robots.txt"):
            return 0, ROBOTS
        if url.endswith("/portal-rrhh"):
            return 0, PORTAL
        if url.endswith("/backup/rrhh.conf"):
            return 0, BACKUP
        return 0, ROBOTS
    return ejecutar


def cadena():
    return [AgenteRecon(), AgenteEnum(), AgenteFoothold(), AgenteLoot(), AgenteImpacto()]


def corrida(ruta, agentes):
    llamadas = []
    b = Bitacora(ruta, CLAVE)
    pizarra = correr(agentes, b, falso(llamadas))
    return b, pizarra, llamadas


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read().splitlines()


def escribir(ruta, lineas):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("".join(l + "\n" for l in lineas))


with tempfile.TemporaryDirectory() as d:
    r1, r2 = os.path.join(d, "a.jsonl"), os.path.join(d, "b.jsonl")
    b1, pizarra, llamadas = corrida(r1, [AgenteRecon(), AgenteEnum()])
    b2, _, _ = corrida(r2, [AgenteRecon(), AgenteEnum()])

    assert b1.ultimo == b2.ultimo, "dos corridas iguales tienen que dar la misma cabeza"
    assert leer(r1) == leer(r2), "y la misma bitácora byte a byte"
    with open(r1, "rb") as f:
        assert b"\r" not in f.read(), "fin de línea LF en todos los sistemas operativos"

    assert pizarra["puertos"] == {22: "ssh", 80: "http?"}, "así marca nmap un HTTP sin fingerprint"
    assert hallazgos_http(pizarra) == {(80, "/interno"): 200, (80, "/portal-rrhh"): 200}, \
        "la ruta que robots.txt esconde también se prueba"
    assert len(llamadas) == 1 + 1 + 7 + 1, "nmap, robots.txt, 7 de la lista fija y la ruta de robots"
    assert all(a[-1].startswith("phantomcorp") or "//phantomcorp:" in a[-1] for a in llamadas)
    assert not any(";" in a[-1] for a in llamadas), "una ruta maliciosa de robots.txt nunca llega al sandbox"

    assert verificar(r1, CLAVE) == b1.ultimo
    try:
        verificar(r1, b"otra-clave")
        raise AssertionError("con otra clave la cadena no puede validar")
    except ValueError:
        pass

    lineas = leer(r1)
    i = max(n for n, l in enumerate(lineas) if '"salida": "404"' in l)
    escribir(r2, lineas[:i] + [lineas[i].replace('"404"', '"200"')] + lineas[i + 1:])
    try:
        verificar(r2, CLAVE)
        raise AssertionError("alterar una línea del medio tiene que romper la cadena")
    except ValueError as e:
        assert f"{i + 1} y {i + 2}" in str(e), e

    escribir(r2, lineas[:-1])
    assert verificar(r2, CLAVE) != b1.ultimo, "truncar el final se detecta contra la cabeza publicada"
    escribir(r2, lineas[:-1] + [lineas[-1].replace(": ", ":  ", 1)])
    assert verificar(r2, CLAVE) != b1.ultimo, "alterar la última línea también"

    try:
        Bitacora(r1, CLAVE)
        raise AssertionError("una bitácora existente nunca se reutiliza")
    except FileExistsError:
        pass

    r3 = os.path.join(d, "c.jsonl")
    _, _, llamadas = corrida(r3, [AgentePicaro()])
    assert llamadas == [], "nada fuera de la RoE llega al sandbox"
    eventos = [json.loads(l) for l in leer(r3)]
    assert [e["evento"] for e in eventos] == ["rechazada"] * 4
    assert [e["datos"]["motivo"].split(":")[0] for e in eventos] == [
        "fuera de alcance", "parámetro inválido", "herramienta no permitida", "puerto inválido"]

    # Cadena completa R1–R4 contra el sandbox falso: determinista y con las 4 flags.
    rc1, rc2 = os.path.join(d, "full1.jsonl"), os.path.join(d, "full2.jsonl")
    bc1, piz, _ = corrida(rc1, cadena())
    bc2, _, _ = corrida(rc2, cadena())
    assert leer(rc1) == leer(rc2) and bc1.ultimo == bc2.ultimo, "la cadena completa también es determinista"
    assert piz.get("foothold") and piz.get("impacto"), "R2 y R4 dejaron resultado en la pizarra"
    assert piz.get("token") == "phantom-api-7c1e", "R3 looteó el token del backup de config"
    assert piz.get("flags") == ["FLAG{demo_recon}", "FLAG{demo_foothold}", "FLAG{demo_token}", "FLAG{demo_crown}"], \
        "las 4 flags salen en el orden de la cadena"

    # El catálogo es la única vía para explotar: un PoC inventado o cruzado no pasa la RoE.
    for mala, motivo in [
        (Accion("x", "curl_post", "phantomcorp", 80, "/portal/login"), "PoC fuera del catálogo"),
        (Accion("x", "curl_post", "phantomcorp", 80, "/portal/login", poc="inventado"), "PoC fuera del catálogo"),
        (Accion("x", "curl_api", "phantomcorp", 80, "/api/reporte", poc="sqli-bypass-login", token="t"), "no es de"),
        (Accion("x", "curl_api", "phantomcorp", 80, "/api/reporte", poc="rce-leer-joyas", token="mal/token"), "token inválido"),
    ]:
        try:
            validar(mala)
            raise AssertionError(f"la RoE dejó pasar una acción que tenía que rechazar: {mala}")
        except PermissionError as e:
            assert motivo in str(e), e
    argv = validar(Accion("x", "curl_post", "phantomcorp", 80, "/portal/login", poc="sqli-bypass-login"))
    assert "--data" in argv and "user=admin'-- -&pass=x" in argv, "el payload lo pone el catálogo, no el agente"

    alt = panel.demo_alteracion(pathlib.Path(r1), CLAVE)
    assert alt["detectada"] and f"{alt['linea']} y {alt['linea'] + 1}" in alt["mensaje"], alt
    assert verificar(r1, CLAVE) == b1.ultimo, "la demo de alteración nunca toca el original"

    loot_real, panel.LOOT = panel.LOOT, pathlib.Path(d)
    panel.probar_roe({"nombre": "roe.jsonl", "clave": "k"})
    assert [e["evento"] for e in panel.leer_eventos(pathlib.Path(d, "roe.jsonl"))] == ["rechazada"] * 4, \
        "el botón «Probar la RoE» del panel tiene que terminar con todo rechazado"
    panel.LOOT = loot_real

    if shutil.which("openssl"):
        prev = "0" * 64
        for linea in lineas:
            assert json.loads(linea)["prev"] == prev
            out = subprocess.run(["openssl", "dgst", "-sha256", "-hmac", CLAVE.decode()],
                                 input=linea.encode("utf-8"), capture_output=True, check=True)
            prev = out.stdout.decode().split()[-1]
        assert prev == b1.ultimo, "openssl recalcula la misma cabeza"
        print("cadena verificada también con openssl")
    else:
        print("openssl no está en el PATH: se omitió la verificación independiente")

for malo in ("../x.jsonl", "a/b.jsonl", "..\\x.jsonl", "c:x.jsonl", "x.txt", "", None):
    try:
        panel.ruta_bitacora(malo)
        raise AssertionError(f"el panel aceptó un nombre de bitácora peligroso: {malo!r}")
    except ValueError:
        pass
assert panel.ruta_bitacora("bitacora-1.jsonl") == (panel.LOOT / "bitacora-1.jsonl").resolve()

servidor = ThreadingHTTPServer(("127.0.0.1", 0), panel.Panel)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
puerto = servidor.server_address[1]


def pedir(host, token, metodo="GET", ruta="/api/estado", cuerpo=None):
    c = http.client.HTTPConnection("127.0.0.1", puerto, timeout=10)
    headers = {"Host": host, "Content-Type": "application/json"}
    if token is not None:
        headers["X-Token"] = token
    c.request(metodo, ruta, body=cuerpo, headers=headers)
    return c.getresponse().status


propio = f"127.0.0.1:{puerto}"
assert pedir(propio, panel.TOKEN) == 200
assert pedir(propio, None) == 403, "sin token es un pedido de otra página (CSRF)"
assert pedir(propio, "token-adivinado") == 403
assert pedir(f"atacante.example:{puerto}", panel.TOKEN) == 403, "Host ajeno es DNS rebinding"
assert pedir(propio, None, ruta="/") == 200, "la página en sí se sirve sin token"
assert pedir(f"atacante.example:{puerto}", None, ruta="/") == 403, "ni la página a un Host ajeno"
assert pedir(propio, None, "POST", "/api/correr", b'{"nombre": "x.jsonl", "clave": "k"}') == 403
assert pedir(propio, panel.TOKEN, "POST", "/api/correr", b'{"nombre": "../x.jsonl", "clave": "k"}') == 400
servidor.shutdown()

print("OK")
