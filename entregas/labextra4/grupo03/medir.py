#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Mide hash_de() y emite JSON; no modifica el caso ni busca claves de root."""
import argparse
import json
import math
import os
import platform
import ssl
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter

from cracker import ITER_PBKDF2, cargar_candidatos, cargar_sombra, hash_de


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sombra")
    parser.add_argument("diccionario")
    args = parser.parse_args()
    sombra = cargar_sombra(args.sombra)
    palabras = cargar_candidatos(args.diccionario)
    con_reglas = cargar_candidatos(args.diccionario, True)
    if not palabras:
        parser.error("el diccionario debe contener al menos una palabra")
    mediciones = []
    for algo in ("md5", "sha256", "pbkdf2"):
        salt = next(s for _u, a, s, _h in sombra if a == algo)
        cantidad = 20 if algo == "pbkdf2" else 100_000
        # Se preparan antes del cronómetro; sin lectura ni impresión en el bucle.
        candidatos = [palabras[i % len(palabras)] for i in range(cantidad)]
        hash_de(algo, salt, candidatos[0])  # calentamiento fuera de la medición
        tiempos = []
        for _ in range(3):
            inicio = perf_counter()
            for candidato in candidatos:
                hash_de(algo, salt, candidato)
            tiempos.append(perf_counter() - inicio)
        segundos = statistics.median(tiempos)
        tasa = cantidad / segundos
        mediciones.append({
            "algoritmo": algo,
            "iteraciones_pbkdf2": ITER_PBKDF2 if algo == "pbkdf2" else None,
            "intentos_por_repeticion": cantidad,
            "segundos_repeticiones": tiempos,
            "mediana_segundos": segundos,
            "intentos_por_segundo": tasa,
            "segundos_diccionario": len(palabras) / tasa,
            "segundos_con_reglas": len(con_reglas) / tasa,
        })
    tasas = {m["algoritmo"]: m["intentos_por_segundo"] for m in mediciones}
    razon = tasas["md5"] / tasas["pbkdf2"]
    # Las 1.000 unidades siguientes son equivalentes al hilo medido, NO GPUs.
    ideal = len(palabras) / (1000 * tasas["pbkdf2"])
    print(json.dumps({
        "fecha_buenos_aires": datetime.now(timezone(timedelta(hours=-3))).isoformat(),
        "entorno": {"python": platform.python_version(), "sistema": platform.platform(),
                    "procesador": platform.processor(), "cpus_logicas": os.cpu_count(),
                    "openssl": ssl.OPENSSL_VERSION},
        "diccionario": str(Path(args.diccionario)),
        "candidatos_diccionario": len(palabras),
        "candidatos_con_reglas": len(con_reglas),
        "metodo": "Un hilo; perf_counter; mediana de 3 tandas de hash_de; sin I/O en el bucle. No es un benchmark GPU.",
        "mediciones": mediciones,
        "razon_md5_sobre_pbkdf2": razon,
        "ordenes_magnitud_md5_pbkdf2": math.log10(razon),
        "segundos_1000_unidades_equivalentes_cpu_ideal": ideal,
        "advertencia": "Sin medir PBKDF2-200k en una GPU no se puede asignar una tasa real a 1000 GPUs. Además, un diccionario de 49 candidatos no ocupa 1000 GPUs en paralelo.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
