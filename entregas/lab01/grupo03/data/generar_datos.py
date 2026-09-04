#!/usr/bin/env python3
"""
Laboratorio 01 — Generador de datos de muestra.

Seguridad Informática · Unidad 1 · UTN Facultad Regional Villa María · 2026

Crea el directorio `muestra/` con cuatro archivos sobre los que van a probar
`integridad.py`. La salida es DETERMINISTA: dos corridas producen archivos
byte a byte idénticos, y por lo tanto los mismos digests. Eso es a propósito:
si los datos cambiaran en cada corrida, no podrían distinguir una modificación
real de una diferencia del generador.

Este archivo NO hay que modificarlo ni completarlo. Se ejecuta y listo:

    python3 data/generar_datos.py

El directorio `muestra/` está en .gitignore. No lo versionen: es salida, no
fuente. Si el corrector necesita los datos, los regenera con este script.

Los archivos generados incluyen un subdirectorio a propósito, para que el
recorrido de `generar` tenga que ser realmente recursivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

DIRECTORIO_MUESTRA = Path(__file__).resolve().parent / "muestra"


TRANSFERENCIA = """\
ORDEN DE TRANSFERENCIA ELECTRONICA
==================================

Entidad emisora   : Banco Ficticio de Villa Maria S.A.
Sucursal          : 0042 - Villa Maria, Cordoba
Fecha de emision  : 2026-03-09
Numero de orden   : OT-2026-0000417

ORDENANTE
  Titular         : Cooperativa de Servicios Ejemplo Ltda.
  CUIT            : 30-00000000-0
  Cuenta origen   : 0042-00000417-8

BENEFICIARIO
  Titular         : Proveedora Industrial Generica S.R.L.
  CUIT            : 30-11111111-1
  Cuenta destino  : 0107-00009982-3

IMPORTE           : ARS 1.000.000,00
Concepto          : Cancelacion factura A-0001-00003271
Modalidad         : Transferencia inmediata

Autorizada por    : Direccion de Administracion
Estado            : PENDIENTE DE ACREDITACION

-- DOCUMENTO DE PRUEBA --
Datos ficticios generados para el Laboratorio 01 de Seguridad Informatica.
No corresponde a ninguna persona, entidad ni operacion real.

Este archivo es el objetivo de la prueba de deteccion de un solo byte:
agregar un caracter al final debe hacer que `verificar` lo reporte como
MODIFICADO y que el programa termine con codigo de salida 1.
"""


ACCESO_LOG = """\
2026-03-09T08:14:02Z INFO  auth   usuario=jperez     ip=10.20.4.11   accion=login      resultado=exito
2026-03-09T08:15:47Z INFO  files  usuario=jperez     ip=10.20.4.11   accion=read       objeto=/informes/Q1.pdf
2026-03-09T09:02:31Z WARN  auth   usuario=admin      ip=203.0.113.44 accion=login      resultado=fallo intentos=3
2026-03-09T09:02:58Z WARN  auth   usuario=admin      ip=203.0.113.44 accion=login      resultado=fallo intentos=4
2026-03-09T09:03:12Z ERROR auth   usuario=admin      ip=203.0.113.44 accion=login      resultado=bloqueo motivo=umbral_superado
2026-03-09T11:41:09Z INFO  files  usuario=mgonzalez  ip=10.20.4.27   accion=write      objeto=/politicas/seguridad.md
2026-03-09T14:22:55Z INFO  auth   usuario=mgonzalez  ip=10.20.4.27   accion=logout     resultado=exito
2026-03-09T23:58:03Z WARN  files  usuario=svc_backup ip=10.20.9.2    accion=delete     objeto=/tmp/dump.sql
"""


POLITICA = """\
# Politica de Seguridad de la Informacion (extracto de muestra)

> Documento ficticio, generado para el Laboratorio 01 de Seguridad
> Informatica. No refleja la politica de ninguna organizacion real.

## 1. Proposito

Establecer las directrices para preservar la **confidencialidad**, la
**integridad** y la **disponibilidad** de la informacion de la organizacion.

## 2. Alcance

Aplica a todo el personal, a los sistemas de informacion propios y a los
servicios provistos por terceros que procesen informacion de la
organizacion.

## 3. Principios

### 3.1 Confidencialidad
La informacion solo es accesible para quien esta autorizado a conocerla. El
acceso se otorga segun el principio de minimo privilegio: cada persona
recibe unicamente los permisos que su funcion requiere.

### 3.2 Integridad
La informacion es exacta y completa, y solo puede ser modificada mediante
procesos autorizados. Toda modificacion queda registrada de manera que sea
posible determinar quien la realizo y cuando.

### 3.3 Disponibilidad
La informacion y los servicios que la procesan estan accesibles cuando el
proceso de negocio lo requiere, dentro de los niveles de servicio acordados.

## 4. Control de versiones de este documento

Este documento se somete a verificacion periodica de integridad. Cualquier
modificacion no autorizada de su contenido debe ser detectada por el
procedimiento de verificacion vigente.

Version: 1.0
Estado: vigente
"""


def _escribir_texto(ruta: Path, contenido: str) -> None:
    """Escribe texto con fin de linea LF y codificacion UTF-8, siempre igual.

    `newline="\\n"` es importante: sin eso, en Windows Python traduciria cada
    \\n a \\r\\n y el archivo tendria un digest distinto al generado en Linux.
    Un generador de datos de prueba que produce bytes distintos segun el
    sistema operativo arruina cualquier comparacion de hashes.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(contenido)


def _escribir_binario(ruta: Path, contenido: bytes) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)


def generar() -> list[Path]:
    """Crea los archivos de muestra y devuelve la lista de rutas escritas."""
    DIRECTORIO_MUESTRA.mkdir(parents=True, exist_ok=True)

    archivos: list[Path] = []

    ruta = DIRECTORIO_MUESTRA / "transferencia.txt"
    _escribir_texto(ruta, TRANSFERENCIA)
    archivos.append(ruta)

    # En un subdirectorio a proposito: obliga a que el recorrido sea recursivo.
    ruta = DIRECTORIO_MUESTRA / "logs" / "acceso.log"
    _escribir_texto(ruta, ACCESO_LOG)
    archivos.append(ruta)

    ruta = DIRECTORIO_MUESTRA / "politica_seguridad.md"
    _escribir_texto(ruta, POLITICA)
    archivos.append(ruta)

    # Binario determinista: los 256 valores posibles de un byte, repetidos 64
    # veces. Son 16.384 bytes exactos. Sirve para comprobar que el hasheo se
    # hace en modo binario y por bloques, sin decodificar nada como texto.
    ruta = DIRECTORIO_MUESTRA / "app.bin"
    _escribir_binario(ruta, bytes(range(256)) * 64)
    archivos.append(ruta)

    return archivos


def main() -> int:
    archivos = generar()

    print(f"Datos de muestra generados en: {DIRECTORIO_MUESTRA}")
    print()
    for ruta in sorted(archivos):
        relativa = ruta.relative_to(DIRECTORIO_MUESTRA).as_posix()
        print(f"  {relativa:<28} {ruta.stat().st_size:>7} bytes")
    print()
    print(f"Total: {len(archivos)} archivos.")
    print()
    print("Proximo paso:")
    print("  python3 src/integridad.py generar --dir data/muestra --salida manifest.sha256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
