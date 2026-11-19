"""Utilidades comunes de adaptadores: validación de target y ejecución sin shell."""
from __future__ import annotations

import ipaddress
import re
import subprocess
from pathlib import Path
from typing import Callable

import yaml

_HOST_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
_PROFILES = Path(__file__).resolve().parent.parent / "profiles.yaml"


class InvalidTarget(ValueError): ...
class ForbiddenArgument(ValueError): ...


def load_profiles(path: Path = _PROFILES) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_target(target: str, allow_cidr: bool = False) -> str:
    """Acepta IP, CIDR (si allow_cidr) o hostname FQDN. Rechaza todo lo demás
    (espacios, flags que empiecen con '-', metacaracteres de shell, esquemas)."""
    t = target.strip().lower()
    if not t or t.startswith("-"):
        raise InvalidTarget(f"target inválido: {target!r}")
    try:
        ipaddress.ip_address(t)
        return t
    except ValueError:
        pass
    if allow_cidr:
        try:
            ipaddress.ip_network(t, strict=False)
            return t
        except ValueError:
            pass
    if _HOST_RE.match(t):
        return t
    raise InvalidTarget(f"target inválido: {target!r}")


def validate_url(url: str) -> str:
    """Solo http(s)://host[:puerto][/ruta] sin credenciales embebidas."""
    m = re.match(r"^(https?)://([^/:@\s]+)(:\d{1,5})?(/[^\s]*)?$", url.strip())
    if not m:
        raise InvalidTarget(f"URL inválida: {url!r}")
    validate_target(m.group(2))
    return url.strip()


def reject_forbidden(argv: list[str], forbidden: list[str]) -> None:
    for a in argv:
        for f in forbidden:
            if a == f or a.startswith(f + "="):
                raise ForbiddenArgument(f"argumento prohibido: {a}")


Runner = Callable[[list[str], int], str]


def default_runner(argv: list[str], timeout_s: int) -> str:
    """Ejecuta SIN shell, con timeout. Se inyecta un fake en los tests."""
    proc = subprocess.run(argv, shell=False, capture_output=True, text=True,
                          timeout=timeout_s, check=False)
    return proc.stdout
