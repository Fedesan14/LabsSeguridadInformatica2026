#!/usr/bin/env python3
"""
Laboratorio 01 — Verificación de integridad con funciones de hash.

Seguridad Informática · Unidad 1 · UTN Facultad Regional Villa María · 2026

--------------------------------------------------------------------------
QUÉ ES ESTO
--------------------------------------------------------------------------
Una herramienta de línea de comandos para razonar sobre INTEGRIDAD, la "I"
de la tríada CIA: la propiedad que garantiza que un dato no fue alterado de
manera no autorizada.

El mecanismo es el mismo que usan los verificadores de integridad de
archivos (FIM), los gestores de paquetes al validar una descarga y los
sistemas de control de versiones: se calcula el digest de cada archivo y se
lo compara contra un valor registrado previamente.

--------------------------------------------------------------------------
SOBRE SHA-256
--------------------------------------------------------------------------
SHA-256 pertenece a la familia SHA-2, especificada por el NIST en
FIPS PUB 180-4, "Secure Hash Standard (SHS)". Produce un digest de 256 bits
(32 bytes, 64 caracteres en representación hexadecimal).

Las propiedades que nos interesan acá:

  · Determinismo         — la misma entrada produce siempre la misma salida.
  · Unidireccionalidad   — dado el digest, es computacionalmente inviable
                           recuperar la entrada.
  · Resistencia a colisiones — es inviable hallar dos entradas distintas con
                           el mismo digest.
  · Efecto avalancha     — un cambio mínimo en la entrada modifica alrededor
                           de la mitad de los bits de salida.

El subcomando `avalancha` existe justamente para que vean la última con sus
propios ojos, no porque se los cuenten.

--------------------------------------------------------------------------
SOBRE HMAC
--------------------------------------------------------------------------
Un hash a secas prueba que un dato no cambió, pero no prueba QUIÉN lo
calculó: cualquiera puede recalcularlo. HMAC (RFC 2104) incorpora una clave
secreta al cálculo, de modo que solo quien la conoce puede producir un tag
válido. Eso agrega autenticidad del origen.

Qué NO agrega es una de las preguntas del informe. Pensala antes de
escribir el código.

--------------------------------------------------------------------------
CÓMO SE USA
--------------------------------------------------------------------------
    python3 integridad.py --help
    python3 integridad.py generar    --dir ../data/muestra --salida manifest.sha256
    python3 integridad.py verificar  --dir ../data/muestra --manifiesto manifest.sha256
    python3 integridad.py avalancha  --a "mensaje" --b "mensajf"
    python3 integridad.py mac        --clave "secreto" --mensaje "transferir 1000"

--------------------------------------------------------------------------
QUÉ HAY QUE HACER
--------------------------------------------------------------------------
Hay CUATRO bloques marcados con `TODO`, uno por subcomando. Cada uno lanza
`NotImplementedError`. Hay que reemplazarlos por la implementación.

NO modifiquen:
  · las firmas de las funciones,
  · los nombres de los subcomandos ni de sus argumentos,
  · la función `sha256_archivo()`, que está resuelta como referencia.

Restricción: SOLO biblioteca estándar. Nada de `pip install`.
Requiere Python 3.10 o superior.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path

# Tamaño de bloque de lectura: 64 KiB.
#
# Por qué no leer el archivo entero de una: un `ruta.read_bytes()` sobre un
# archivo de 4 GB reserva 4 GB de memoria. Leer por bloques mantiene el uso de
# memoria constante sin importar el tamaño del archivo. Es el patrón estándar
# para hashear archivos y es el que hay que replicar.
TAMANIO_BLOQUE = 64 * 1024

# Nombre por defecto del manifiesto.
MANIFIESTO_POR_DEFECTO = "manifest.sha256"

# Estados posibles de un archivo al verificarlo contra el manifiesto.
ESTADO_OK = "OK"
ESTADO_MODIFICADO = "MODIFICADO"
ESTADO_FALTANTE = "FALTANTE"
ESTADO_NUEVO = "NUEVO"


# ==========================================================================
# FUNCIÓN DE REFERENCIA — ya implementada. Léanla antes de escribir nada.
# ==========================================================================


def sha256_archivo(ruta: Path) -> str:
    """Calcula el digest SHA-256 de un archivo y lo devuelve en hexadecimal.

    Esta función está resuelta a propósito: muestra el patrón de lectura por
    bloques que hay que usar. Fijate en tres cosas:

      1. El archivo se abre en modo binario (`"rb"`). Nunca en modo texto:
         el modo texto aplica decodificación y traducción de fin de línea, y
         eso cambiaría el digest según el sistema operativo.
      2. Se acumula con `hasher.update()` en un bucle, en vez de cargar todo
         en memoria.
      3. `hexdigest()` devuelve la representación hexadecimal; `digest()`
         devolvería los bytes crudos. Los vas a necesitar en `avalancha`.

    Args:
        ruta: ruta al archivo a hashear.

    Returns:
        El digest SHA-256 en hexadecimal, 64 caracteres en minúscula.
    """
    hasher = hashlib.sha256()
    with ruta.open("rb") as archivo:
        while bloque := archivo.read(TAMANIO_BLOQUE):
            hasher.update(bloque)
    return hasher.hexdigest()


# ==========================================================================
# TODO 1 de 4 — subcomando `generar`
# ==========================================================================


def generar_manifiesto(directorio: Path, salida: Path) -> dict[str, str]:
    """Recorre `directorio` recursivamente y devuelve el manifiesto de hashes.

    El manifiesto es un diccionario que mapea la ruta relativa de cada
    archivo a su digest SHA-256:

        {
          "app.bin": "a3f5...",
          "logs/acceso.log": "9c21...",
          "politica_seguridad.md": "77be..."
        }

    Requisitos (se evalúan):

      · Recorrido RECURSIVO: hay que entrar en los subdirectorios.
      · Rutas RELATIVAS a `directorio`, no absolutas. Un manifiesto con rutas
        absolutas solo sirve en la máquina donde se generó.
      · Rutas en formato POSIX: separador `/`, no `\\`. Un manifiesto generado
        en Windows tiene que poder verificarse en Linux.
      · Claves ORDENADAS alfabéticamente. Un manifiesto se versiona y se
        compara con `diff`; si el orden cambia entre corridas, el diff es
        ruido.
      · El propio archivo de salida NO debe incluirse, si queda dentro del
        directorio recorrido. Pensá por qué: incluirlo es imposible, el
        digest cambiaría al escribirlo.
      · Solo archivos regulares. Los directorios no se hashean.

    Args:
        directorio: directorio base a recorrer.
        salida: ruta del archivo de manifiesto que se va a escribir. Se
            recibe acá para poder excluirlo del recorrido.

    Returns:
        Diccionario {ruta_relativa_posix: digest_hexadecimal}, ordenado.

    Pistas:
        · `Path.rglob("*")` recorre recursivamente. Devuelve archivos Y
          directorios: filtrá con `Path.is_file()`.
        · `Path.relative_to(base)` te da la ruta relativa.
        · `PurePath.as_posix()` fuerza el separador `/`.
        · Para comparar si dos rutas son la misma, `Path.resolve()` normaliza
          ambas antes de compararlas.
        · `dict(sorted(d.items()))` devuelve el diccionario ordenado por
          clave. Desde Python 3.7 los diccionarios preservan el orden de
          inserción, así que esto alcanza.
        · Reusá `sha256_archivo()`. No reescribas el bucle de lectura.
    """
    # ----------------------------------------------------------------------
    # TODO 1: implementar el recorrido y la construcción del manifiesto.
    #         Borrá el `raise` de abajo y escribí tu código.
    # ----------------------------------------------------------------------
    raise NotImplementedError(
        "TODO 1 de 4 — generar_manifiesto() sin implementar.\n"
        "  Qué falta: recorrer el directorio recursivamente y devolver el\n"
        "  diccionario {ruta_relativa_posix: digest_sha256}, ordenado por clave.\n"
        "  Leé el docstring de esta función: están los requisitos y las pistas."
    )


# ==========================================================================
# TODO 2 de 4 — subcomando `verificar`
# ==========================================================================


def verificar_manifiesto(
    directorio: Path, manifiesto: dict[str, str], ruta_manifiesto: Path
) -> dict[str, list[str]]:
    """Contrasta el estado actual de `directorio` contra `manifiesto`.

    Clasifica cada archivo en exactamente una de cuatro categorías:

        OK          — está en el manifiesto y el digest coincide.
        MODIFICADO  — está en el manifiesto y el digest NO coincide.
        FALTANTE    — está en el manifiesto pero ya no existe en el disco.
        NUEVO       — existe en el disco pero no está en el manifiesto.

    Las cuatro importan. Es tentador implementar solo MODIFICADO, pero
    FALTANTE detecta un borrado y NUEVO detecta un archivo plantado por un
    atacante. Un verificador que solo mira lo que ya conocía es ciego
    justamente a lo que le agregaron.

    Args:
        directorio: directorio a verificar.
        manifiesto: el manifiesto ya cargado, {ruta_relativa: digest}.
        ruta_manifiesto: ruta del archivo de manifiesto en disco. Se recibe
            para poder excluirlo del recorrido si quedó dentro de
            `directorio`; si no, se reportaría como NUEVO en cada corrida.

    Returns:
        Diccionario con exactamente estas cuatro claves, cada una con la
        lista ORDENADA de rutas relativas en esa categoría:

            {
              "OK":         ["app.bin", "politica_seguridad.md"],
              "MODIFICADO": ["transferencia.txt"],
              "FALTANTE":   [],
              "NUEVO":      ["backdoor.sh"]
            }

        Usá las constantes ESTADO_OK, ESTADO_MODIFICADO, ESTADO_FALTANTE y
        ESTADO_NUEVO como claves. El código que imprime el informe y calcula
        el código de salida ya está escrito y espera esta estructura exacta.

    Pistas:
        · Armá primero el conjunto de rutas del disco, igual que en `generar`.
          Después trabajá con operaciones de conjuntos:
              en_ambos   = del_disco & del_manifiesto
              solo_disco = del_disco - del_manifiesto   ->  NUEVO
              solo_manif = del_manifiesto - del_disco   ->  FALTANTE
        · Para las rutas que están en ambos, recalculá el digest y comparalo
          con el registrado: define OK contra MODIFICADO.
        · Excluí el archivo de manifiesto del recorrido, igual que en TODO 1,
          o se va a reportar como NUEVO en cada corrida.
        · Devolvé SIEMPRE las cuatro claves, aunque alguna lista quede vacía.
          Un consumidor que tiene que hacer `.get(clave, [])` es un consumidor
          al que le pasaste un contrato flojo.
    """
    # ----------------------------------------------------------------------
    # TODO 2: implementar la clasificación en OK / MODIFICADO / FALTANTE / NUEVO.
    #         Borrá el `raise` de abajo y escribí tu código.
    # ----------------------------------------------------------------------
    raise NotImplementedError(
        "TODO 2 de 4 — verificar_manifiesto() sin implementar.\n"
        "  Qué falta: comparar el directorio contra el manifiesto y devolver\n"
        "  el diccionario con las cuatro categorías OK/MODIFICADO/FALTANTE/NUEVO.\n"
        "  Leé el docstring de esta función: está la estructura exacta esperada."
    )


# ==========================================================================
# TODO 3 de 4 — subcomando `avalancha`
# ==========================================================================


def distancia_hamming_bits(digest_a: bytes, digest_b: bytes) -> int:
    """Devuelve la cantidad de BITS en que difieren dos digests.

    Esta es la medición que hace visible el efecto avalancha: dos mensajes
    que difieren en un solo carácter producen digests que difieren en
    aproximadamente la mitad de sus 256 bits.

    ATENCIÓN — el error más común de este laboratorio:

        La distancia se mide en BITS, no en caracteres hexadecimales.

        Dos dígitos hexadecimales distintos pueden diferir en 1 bit o en 4.
        Comparar `'a' != 'b'` cuenta una diferencia donde en realidad hay
        tres bits distintos (0xa = 1010, 0xb = 1011 difieren en 1 bit;
        0x0 = 0000 y 0xf = 1111 difieren en 4). Si contás caracteres, el
        número te va a dar sistemáticamente mal y el ejercicio pierde todo
        su sentido.

        Trabajá sobre los BYTES CRUDOS, no sobre la cadena hexadecimal.

    Args:
        digest_a: primer digest, en bytes crudos (32 bytes para SHA-256).
        digest_b: segundo digest, en bytes crudos, del mismo largo.

    Returns:
        Cantidad de bits en que difieren. Entre 0 y 256 para SHA-256.

    Raises:
        ValueError: si los digests tienen distinto largo. Comparar dos
            digests de largo distinto no tiene sentido y hay que decirlo, no
            devolver un número inventado.

    Pistas:
        · `hashlib.sha256(datos).digest()` devuelve los bytes crudos.
          `hexdigest()` devuelve la cadena. Acá querés `digest()`.
        · Recorrer dos secuencias en paralelo: `zip(a, b)`.
        · El XOR (`^`) de dos bytes tiene un bit en 1 exactamente en las
          posiciones donde los operandos difieren. Ese es el truco central.
        · `int.bit_count()` cuenta los bits en 1 de un entero (Python 3.10+).
          Si estás en una versión anterior: `bin(n).count("1")`.
    """
    # ----------------------------------------------------------------------
    # TODO 3: implementar la distancia de Hamming EN BITS.
    #         Borrá el `raise` de abajo y escribí tu código.
    # ----------------------------------------------------------------------
    raise NotImplementedError(
        "TODO 3 de 4 — distancia_hamming_bits() sin implementar.\n"
        "  Qué falta: contar en cuántos BITS (no caracteres hex) difieren\n"
        "  los dos digests recibidos como bytes crudos.\n"
        "  Leé el docstring de esta función: la advertencia sobre bits vs. hex\n"
        "  es el punto del ejercicio."
    )


# ==========================================================================
# TODO 4 de 4 — subcomando `mac`
# ==========================================================================


def calcular_mac(clave: bytes, mensaje: bytes, tag_esperado: str | None = None) -> tuple[str, bool | None]:
    """Calcula un HMAC-SHA256 y, opcionalmente, verifica un tag recibido.

    HMAC está especificado en el RFC 2104 (Krawczyk, Bellare y Canetti).
    Combina una función de hash con una clave secreta de forma tal que un
    atacante que no conoce la clave no puede producir un tag válido, aun
    conociendo el mensaje y la función de hash usada.

    Dos reglas que NO se negocian en esta implementación:

      1. Usá el módulo `hmac` de la biblioteca estándar. No implementen HMAC
         a mano con los paddings ipad/opad. El objetivo del ejercicio es
         entender QUÉ resuelve HMAC, no reescribir el estándar — y una
         implementación casera de criptografía es, en producción, una
         vulnerabilidad esperando su turno.

      2. La comparación del tag DEBE hacerse con `hmac.compare_digest()`.
         Nunca con `==`. El porqué es la pregunta 4 del informe: contestala
         antes de escribir esta línea, no después.

    Args:
        clave: clave secreta, en bytes.
        mensaje: mensaje a autenticar, en bytes.
        tag_esperado: tag en hexadecimal a verificar. Si es None, solo se
            calcula.

    Returns:
        Una tupla `(tag_calculado, resultado_verificacion)` donde:
          · `tag_calculado` es el HMAC-SHA256 en hexadecimal;
          · `resultado_verificacion` es True si `tag_esperado` coincide,
            False si no coincide, y None si no se pidió verificación.

    Pistas:
        · `hmac.new(clave, mensaje, hashlib.sha256)` construye el objeto;
          `.hexdigest()` te da el tag en hexadecimal.
        · `hmac.compare_digest(a, b)` acepta dos `str` de ASCII o dos
          `bytes`. Devuelve un bool.
        · Cuidado con el orden: si `tag_esperado` es None hay que devolver
          None en la segunda posición, no False. "No verifiqué" y "verifiqué
          y dio mal" son cosas distintas, y confundirlas en un sistema de
          seguridad es exactamente cómo se construye un falso negativo.
    """
    # ----------------------------------------------------------------------
    # TODO 4: implementar el cálculo del HMAC-SHA256 y la verificación
    #         en tiempo constante.
    #         Borrá el `raise` de abajo y escribí tu código.
    # ----------------------------------------------------------------------
    raise NotImplementedError(
        "TODO 4 de 4 — calcular_mac() sin implementar.\n"
        "  Qué falta: calcular el HMAC-SHA256 del mensaje con la clave y,\n"
        "  si se pasó --verificar, comparar contra el tag esperado usando\n"
        "  hmac.compare_digest().\n"
        "  Leé el docstring de esta función: la comparación con == está prohibida."
    )


# ==========================================================================
# A partir de acá está todo implementado. No hace falta modificarlo.
# Igual conviene leerlo: acá se ve qué estructura de datos espera recibir
# cada una de las funciones de arriba.
# ==========================================================================


def _cargar_manifiesto(ruta: Path) -> dict[str, str]:
    """Carga un manifiesto desde disco, con mensajes de error legibles."""
    if not ruta.is_file():
        _salir_con_error(
            f"no se encontró el manifiesto '{ruta}'.\n"
            f"  Generalo primero con:  integridad.py generar --dir <dir> --salida {ruta}"
        )
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _salir_con_error(f"el manifiesto '{ruta}' no es JSON válido: {exc}")

    if not isinstance(datos, dict):
        _salir_con_error(f"el manifiesto '{ruta}' debería contener un objeto JSON.")
    return datos


def _validar_directorio(ruta: Path) -> Path:
    """Valida que la ruta exista y sea un directorio."""
    if not ruta.exists():
        _salir_con_error(
            f"el directorio '{ruta}' no existe.\n"
            "  ¿Generaste los datos de muestra?  python3 data/generar_datos.py"
        )
    if not ruta.is_dir():
        _salir_con_error(f"'{ruta}' existe pero no es un directorio.")
    return ruta


def _salir_con_error(mensaje: str) -> None:
    """Imprime un error en stderr y termina con código 2."""
    print(f"error: {mensaje}", file=sys.stderr)
    raise SystemExit(2)


def _cmd_generar(args: argparse.Namespace) -> int:
    directorio = _validar_directorio(Path(args.dir))
    salida = Path(args.salida)

    manifiesto = generar_manifiesto(directorio, salida)

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(manifiesto, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Manifiesto generado: {salida}")
    print(f"Directorio base:     {directorio}")
    print(f"Archivos indexados:  {len(manifiesto)}")
    return 0


def _cmd_verificar(args: argparse.Namespace) -> int:
    directorio = _validar_directorio(Path(args.dir))
    ruta_manifiesto = Path(args.manifiesto)
    manifiesto = _cargar_manifiesto(ruta_manifiesto)

    resultado = verificar_manifiesto(directorio, manifiesto, ruta_manifiesto)

    faltan = [c for c in (ESTADO_OK, ESTADO_MODIFICADO, ESTADO_FALTANTE, ESTADO_NUEVO) if c not in resultado]
    if faltan:
        _salir_con_error(
            "verificar_manifiesto() no devolvió todas las categorías esperadas.\n"
            f"  Faltan: {', '.join(faltan)}\n"
            "  Revisá el docstring: hay que devolver las cuatro claves siempre,\n"
            "  aunque la lista quede vacía."
        )

    print(f"Directorio:  {directorio}")
    print(f"Manifiesto:  {ruta_manifiesto}")
    print()
    print(f"  {ESTADO_OK:<11} {len(resultado[ESTADO_OK]):>4}")
    print(f"  {ESTADO_MODIFICADO:<11} {len(resultado[ESTADO_MODIFICADO]):>4}")
    print(f"  {ESTADO_FALTANTE:<11} {len(resultado[ESTADO_FALTANTE]):>4}")
    print(f"  {ESTADO_NUEVO:<11} {len(resultado[ESTADO_NUEVO]):>4}")

    hallazgos = 0
    for estado in (ESTADO_MODIFICADO, ESTADO_FALTANTE, ESTADO_NUEVO):
        for ruta in resultado[estado]:
            if hallazgos == 0:
                print("\nHallazgos:")
            print(f"  [{estado}] {ruta}")
            hallazgos += 1

    print()
    if hallazgos:
        print(f"INTEGRIDAD COMPROMETIDA — {hallazgos} hallazgo(s).")
        return 1

    print("INTEGRIDAD VERIFICADA — sin diferencias contra el manifiesto.")
    return 0


def _cmd_avalancha(args: argparse.Namespace) -> int:
    bytes_a = args.a.encode("utf-8")
    bytes_b = args.b.encode("utf-8")

    digest_a = hashlib.sha256(bytes_a).digest()
    digest_b = hashlib.sha256(bytes_b).digest()

    distancia = distancia_hamming_bits(digest_a, digest_b)
    total_bits = len(digest_a) * 8
    porcentaje = (distancia / total_bits) * 100 if total_bits else 0.0

    print(f'mensaje A: "{args.a}"')
    print(f"  SHA-256: {digest_a.hex()}")
    print(f'mensaje B: "{args.b}"')
    print(f"  SHA-256: {digest_b.hex()}")
    print()
    print(f"Distancia de Hamming: {distancia} de {total_bits} bits ({porcentaje:.2f} %)")

    if bytes_a == bytes_b:
        print("Los mensajes son idénticos: la distancia tiene que ser 0.")
    else:
        print("Efecto avalancha: para entradas distintas se espera un valor cercano al 50 %.")
    return 0


def _cmd_mac(args: argparse.Namespace) -> int:
    clave = args.clave.encode("utf-8")
    mensaje = args.mensaje.encode("utf-8")

    tag, verificacion = calcular_mac(clave, mensaje, args.verificar)

    print(f'mensaje:      "{args.mensaje}"')
    print(f"HMAC-SHA256:  {tag}")

    if args.verificar is None:
        return 0

    print(f"tag recibido: {args.verificar}")
    print()
    if verificacion:
        print("TAG VÁLIDO — el mensaje es auténtico e íntegro.")
        return 0

    print("TAG INVÁLIDO — el mensaje fue alterado o la clave no es la correcta.")
    return 1


def construir_parser() -> argparse.ArgumentParser:
    """Arma el parser de la CLI. Esta función ya está completa."""
    parser = argparse.ArgumentParser(
        prog="integridad.py",
        description="Laboratorio 01 — Verificación de integridad con funciones de hash.",
        epilog=(
            "Ejemplos:\n"
            "  integridad.py generar   --dir data/muestra --salida manifest.sha256\n"
            "  integridad.py verificar --dir data/muestra --manifiesto manifest.sha256\n"
            '  integridad.py avalancha --a "transferencia: $1000" --b "transferencia: $1001"\n'
            '  integridad.py mac       --clave "secreto" --mensaje "transferir 1000"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subcomandos = parser.add_subparsers(dest="comando", metavar="<subcomando>")

    p_generar = subcomandos.add_parser(
        "generar",
        help="genera el manifiesto de hashes de un directorio",
        description=(
            "Recorre un directorio recursivamente y escribe un manifiesto JSON "
            "que asocia cada ruta relativa con su digest SHA-256."
        ),
    )
    p_generar.add_argument("--dir", required=True, metavar="RUTA", help="directorio a indexar")
    p_generar.add_argument(
        "--salida",
        default=MANIFIESTO_POR_DEFECTO,
        metavar="ARCHIVO",
        help=f"archivo de manifiesto a escribir (por defecto: {MANIFIESTO_POR_DEFECTO})",
    )
    p_generar.set_defaults(func=_cmd_generar)

    p_verificar = subcomandos.add_parser(
        "verificar",
        help="verifica un directorio contra un manifiesto",
        description=(
            "Contrasta el estado actual del directorio contra el manifiesto y "
            "clasifica cada archivo en OK, MODIFICADO, FALTANTE o NUEVO. "
            "Termina con código 1 si hay al menos un hallazgo."
        ),
    )
    p_verificar.add_argument("--dir", required=True, metavar="RUTA", help="directorio a verificar")
    p_verificar.add_argument(
        "--manifiesto",
        default=MANIFIESTO_POR_DEFECTO,
        metavar="ARCHIVO",
        help=f"manifiesto de referencia (por defecto: {MANIFIESTO_POR_DEFECTO})",
    )
    p_verificar.set_defaults(func=_cmd_verificar)

    p_avalancha = subcomandos.add_parser(
        "avalancha",
        help="mide el efecto avalancha entre dos mensajes",
        description=(
            "Calcula la distancia de Hamming EN BITS entre los digests SHA-256 "
            "de dos mensajes, para evidenciar el efecto avalancha."
        ),
    )
    p_avalancha.add_argument("--a", required=True, metavar="TEXTO", help="primer mensaje")
    p_avalancha.add_argument("--b", required=True, metavar="TEXTO", help="segundo mensaje")
    p_avalancha.set_defaults(func=_cmd_avalancha)

    p_mac = subcomandos.add_parser(
        "mac",
        help="calcula o verifica un HMAC-SHA256",
        description=(
            "Calcula el HMAC-SHA256 (RFC 2104) de un mensaje con una clave. "
            "Con --verificar, compara contra un tag recibido usando comparación "
            "en tiempo constante."
        ),
    )
    p_mac.add_argument("--clave", required=True, metavar="TEXTO", help="clave secreta")
    p_mac.add_argument("--mensaje", required=True, metavar="TEXTO", help="mensaje a autenticar")
    p_mac.add_argument(
        "--verificar",
        default=None,
        metavar="TAG",
        help="tag en hexadecimal a verificar contra el calculado",
    )
    p_mac.set_defaults(func=_cmd_mac)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "comando", None):
        parser.print_help()
        return 2

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
