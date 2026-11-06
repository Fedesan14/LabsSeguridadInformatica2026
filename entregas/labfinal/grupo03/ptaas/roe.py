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


@dataclass(frozen=True)
class Accion:
    agente: str
    herramienta: str
    objetivo: str
    puerto: int = 80
    param: str = ""


HERRAMIENTAS = {
    # -sT (connect scan) no necesita NET_RAW: el sandbox corre con --cap-drop ALL.
    # --version-light: contra un servicio sin fingerprint conocido, -sV completo
    # prueba todas las sondas y tarda ~90 s (medido contra phantomcorp); así, ~11 s.
    "nmap": lambda a: ["nmap", "-sT", "-sV", "--version-light", "-Pn", "--top-ports", "100", a.objetivo],
    # Sólo el código HTTP: la acción es de enumeración, no descarga contenido.
    "curl": lambda a: ["curl", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}",
                       f"http://{a.objetivo}:{a.puerto}{a.param}"],
    # Lee el cuerpo de una página (robots.txt). El tope de tamaño evita que el target llene la bitácora.
    "curl_cuerpo": lambda a: ["curl", "-s", "-m", "10", "--max-filesize", "65536",
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
    return HERRAMIENTAS[a.herramienta](a)
