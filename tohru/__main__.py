"""``python -m tohru CODIGO...``: dice qué es cada código sin abrir un intérprete.

Pensado para probar etiquetas a mano con el lector: pegas lo que llegó y ves
si es pesable (PLU y peso), de identidad (prefijo, PLU, secuencia) o nada.
"""

from __future__ import annotations

import sys

from .ean13 import es_valido, solo_digitos
from .identidad import descomponer
from .lector import variantes
from .pesable import decodificar


def describir(codigo: str) -> str:
    """Una línea por código. Prueba identidad primero porque es más estricta."""
    ean = solo_digitos(codigo)
    # decodificar() no mira el verificador a propósito (los lectores a veces
    # no lo mandan); aquí sí, porque si tecleas 13 dígitos quieres saberlo
    if len(ean) == 13 and not es_valido(ean):
        return "inválido   verificador incorrecto"
    ident = descomponer(codigo)
    if ident is not None:
        prefijo, plu, secuencia = ident
        return f"identidad  prefijo={prefijo} plu={plu} secuencia={secuencia}"
    pes = decodificar(codigo)
    if pes is not None:
        return f"pesable    prefijo={pes.prefijo} plu={pes.plu} peso={pes.peso_kg:g} kg"
    if len(ean) == 13:
        return "ean13      válido pero no es de báscula"
    # TODO: con 11 o 12 dígitos habría que decir también qué variante
    # sí cuadra, no solo listarlas
    otras = [v for v in variantes(codigo) if v != codigo]
    if otras:
        return "inválido   quizá el lector lo mutiló; prueba " + " ".join(otras)
    return "inválido"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print("uso: python -m tohru CODIGO [CODIGO...]", file=sys.stderr)
        return 2
    fallos = 0
    for codigo in args:
        linea = describir(codigo)
        print(f"{codigo}  {linea}")
        if linea.startswith("inválido"):
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
