"""Bitácora append-only, encadenada con HMAC-SHA256.

Cada línea guarda el HMAC de la línea anterior en `prev`. Alterar la línea k
rompe la cadena en la k+1; alterar o truncar el final no rompe nada hacia
atrás, por eso `verificar` devuelve la cabeza y hay que compararla con la que
el orquestador publicó al terminar (va en el informe).

HMAC y no SHA-256 a secas: con un hash sin clave, quien edite el archivo puede
recalcular la cadena entera. La clave vive en el orquestador, nunca en los
agentes ni en el sandbox.
"""
import hashlib
import hmac
import json
import os
import sys

GENESIS = "0" * 64


def _mac(clave: bytes, linea: str) -> str:
    return hmac.new(clave, linea.encode("utf-8"), hashlib.sha256).hexdigest()


class Bitacora:
    def __init__(self, ruta, clave: bytes):
        if not clave:
            raise ValueError("la clave de la bitácora no puede estar vacía")
        # "x" falla si el archivo existe: nunca se pisa ni se mezcla una corrida anterior.
        open(ruta, "x", encoding="utf-8").close()
        self.ruta, self.clave, self.ultimo = ruta, clave, GENESIS

    def registrar(self, paso, agente, evento, datos):
        # sort_keys da una serialización canónica: sin eso, dos corridas iguales
        # podrían producir cadenas distintas.
        linea = json.dumps({"paso": paso, "agente": agente, "evento": evento,
                            "datos": datos, "prev": self.ultimo},
                           sort_keys=True, ensure_ascii=False)
        # newline="\n": en Windows el modo texto escribe CRLF, y la misma corrida
        # daría bytes distintos según el sistema operativo.
        with open(self.ruta, "a", encoding="utf-8", newline="\n") as f:
            f.write(linea + "\n")
        self.ultimo = _mac(self.clave, linea)


def verificar(ruta, clave: bytes) -> str:
    """Devuelve la cabeza de la cadena o lanza ValueError donde se rompe."""
    prev = GENESIS
    with open(ruta, encoding="utf-8") as f:
        for n, linea in enumerate(f, 1):
            linea = linea.rstrip("\n")
            try:
                recibido = str(json.loads(linea).get("prev"))
            except (ValueError, AttributeError):
                raise ValueError(f"línea {n} ilegible") from None
            if not hmac.compare_digest(recibido.encode(), prev.encode()):
                raise ValueError(f"cadena rota entre las líneas {n - 1} y {n}")
            prev = _mac(clave, linea)
    return prev


if __name__ == "__main__":
    print(verificar(sys.argv[1], os.environ["PTAAS_CLAVE"].encode()))
