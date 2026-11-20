"""Agentes del swarm. Cada uno es un par de funciones sobre la pizarra compartida:

- `proponer(pizarra)` es pura: mismo estado, mismas acciones, en el mismo orden.
  Eso es lo que hace determinista al swarm.
- `interpretar(accion, salida, pizarra)` vuelca lo aprendido en la pizarra.

Los agentes no se conocen entre sí: el hallazgo de uno es lo que activa al
siguiente (patrón blackboard). Nunca ejecutan nada; sólo proponen `Accion`.
"""
import re

from roe import OBJETIVO, Accion

PUERTO_ABIERTO = re.compile(r"^(\d+)/tcp\s+open\s+(\S+)", re.MULTILINE)
WORDLIST = ("/admin", "/interno", "/portal", "/intranet", "/login", "/api", "/backup")
DISALLOW = re.compile(r"^Disallow:\s*(\S+)", re.MULTILINE | re.IGNORECASE)
FLAG = re.compile(r"FLAG\{[^}]+\}")
ACTION = re.compile(r'action=["\']?(/[\w./-]*)')       # action del <form> del portal
BACKUP = re.compile(r"/backup/[\w./-]+")               # ruta del backup que revela el dashboard
API_TOKEN = re.compile(r"API_TOKEN=([\w-]+)")          # token que vive en el backup de config


def _guardar_flags(pizarra, salida):
    """Junta las FLAG{...} que aparezcan en una respuesta: son la evidencia de cada hito."""
    for f in FLAG.findall(salida):
        pizarra.setdefault("flags", [])
        if f not in pizarra["flags"]:
            pizarra["flags"].append(f)


def _portal_login(pizarra):
    """Primer endpoint 200 que parece un portal: lo que enum encontró en R1."""
    for (puerto, ruta), codigo in sorted(pizarra.get("http", {}).items()):
        if codigo == 200 and "portal" in ruta:
            return puerto, ruta
    return None


def rutas_robots(cuerpo):
    """Rutas que robots.txt le pide a los buscadores que no indexen: el sitio las esconde, nosotros las probamos.

    El contenido viene del target, así que es dato no confiable: estas rutas
    pasan por la RoE igual que las de la lista fija.
    """
    return DISALLOW.findall(cuerpo)


class AgenteRecon:
    nombre = "recon"

    def proponer(self, pizarra):
        if "puertos" in pizarra:
            return []
        return [Accion(self.nombre, "nmap", OBJETIVO)]

    def interpretar(self, accion, salida, pizarra):
        pizarra["puertos"] = {int(p): s for p, s in PUERTO_ABIERTO.findall(salida)}


class AgenteEnum:
    """R1: en cada servicio HTTP lee robots.txt y prueba sus rutas junto con la lista fija."""
    nombre = "enum"

    def proponer(self, pizarra):
        vistas = pizarra.get("http", {})
        acciones = []
        for puerto, servicio in sorted(pizarra.get("puertos", {}).items()):
            if "http" not in servicio:
                continue
            if puerto not in pizarra.get("robots", {}):
                # Primero se lee robots.txt: de ahí salen las rutas que faltan probar.
                acciones.append(Accion(self.nombre, "curl_cuerpo", OBJETIVO, puerto, "/robots.txt"))
                continue
            rutas = dict.fromkeys(WORDLIST + tuple(rutas_robots(pizarra["robots"][puerto])))
            acciones += [Accion(self.nombre, "curl", OBJETIVO, puerto, ruta)
                         for ruta in rutas if (puerto, ruta) not in vistas]
        return acciones

    def interpretar(self, accion, salida, pizarra):
        if accion.herramienta == "curl_cuerpo":
            pizarra.setdefault("robots", {})[accion.puerto] = salida
            return
        codigo = int(salida) if salida.strip().isdigit() else 0
        pizarra.setdefault("http", {})[(accion.puerto, accion.param)] = codigo


class AgenteFoothold:
    """R2: con el portal de R1, lee el formulario y prueba la evasión de login por SQLi.

    Dos pasos: primero lee la página (de ahí sale el `action` del form y, de paso,
    la flag de R1 que vive en un comentario HTML); después dispara el PoC del catálogo
    contra ese endpoint. El agente nunca arma el payload: elige un id del catálogo.
    """
    nombre = "foothold"

    def proponer(self, pizarra):
        if pizarra.get("foothold") is not None:
            return []
        portal = _portal_login(pizarra)
        if not portal:
            return []
        if "portal_html" not in pizarra:
            return [Accion(self.nombre, "curl_cuerpo", OBJETIVO, portal[0], portal[1])]
        m = ACTION.search(pizarra["portal_html"])
        ruta = m.group(1) if m else "/portal/login"
        return [Accion(self.nombre, "curl_post", OBJETIVO, portal[0], ruta, poc="sqli-bypass-login")]

    def interpretar(self, accion, salida, pizarra):
        _guardar_flags(pizarra, salida)
        if accion.herramienta == "curl_cuerpo":
            pizarra["portal_html"] = salida
            return
        pizarra["foothold"] = salida
        m = BACKUP.search(salida)
        if m:
            pizarra["backup"] = (accion.puerto, m.group(0))


class AgenteLoot:
    """R3: del dashboard salió una ruta de backup; la lee y saca el token de API."""
    nombre = "loot"

    def proponer(self, pizarra):
        if "token" in pizarra or "backup" not in pizarra:
            return []
        puerto, ruta = pizarra["backup"]
        return [Accion(self.nombre, "curl_cuerpo", OBJETIVO, puerto, ruta)]

    def interpretar(self, accion, salida, pizarra):
        _guardar_flags(pizarra, salida)
        m = API_TOKEN.search(salida)
        if m:
            pizarra["token"] = m.group(1)


class AgenteImpacto:
    """R4: con el token looteado, dispara el PoC de impacto y llega a los datos de clientes."""
    nombre = "impacto"

    def proponer(self, pizarra):
        if "impacto" in pizarra or "token" not in pizarra:
            return []
        puerto = pizarra["backup"][0]
        return [Accion(self.nombre, "curl_api", OBJETIVO, puerto, "/api/reporte",
                       poc="rce-leer-joyas", token=pizarra["token"])]

    def interpretar(self, accion, salida, pizarra):
        pizarra["impacto"] = salida
        _guardar_flags(pizarra, salida)


class AgentePicaro:
    """Agente de demostración: sólo propone acciones que la RoE tiene que rechazar.

    Lo usan el botón «Probar la RoE» del panel y el test. Si alguna de estas
    acciones llegara a ejecutarse, la RoE estaría rota.
    """
    nombre = "picaro"

    def proponer(self, pizarra):
        return [Accion(self.nombre, "curl", "8.8.8.8"),
                Accion(self.nombre, "curl", OBJETIVO, 80, "/x;rm -rf /"),
                Accion(self.nombre, "bash", OBJETIVO),
                Accion(self.nombre, "curl", OBJETIVO, 0)]

    def interpretar(self, *_):
        raise AssertionError("una acción rechazada nunca debería llegar a ejecutarse")


def hallazgos_http(pizarra):
    """Rutas que respondieron algo distinto de 404 (o de no responder)."""
    return {k: c for k, c in pizarra.get("http", {}).items() if c not in (0, 404)}
