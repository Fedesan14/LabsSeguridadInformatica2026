#!/usr/bin/env python3
"""Genera el reto de la Parte B: un texto cifrado con XOR de 1 byte para romper.
Corré: python3 data/generar_datos.py  -> crea data/muestra/reto_xor.hex"""
import os
MENSAJE = ("Memo interno PhantomCorp: la clave del wifi de invitados es "
           "Phantom-Guest-2026. No compartir fuera de la empresa.")
CLAVE = 0x37
def main():
    os.makedirs("data/muestra", exist_ok=True)
    cif = bytes(b ^ CLAVE for b in MENSAJE.encode())
    with open("data/muestra/reto_xor.hex", "w") as f:
        f.write(cif.hex() + "\n")
    print("Creado data/muestra/reto_xor.hex — rompelo con: python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)")
if __name__ == "__main__":
    main()
