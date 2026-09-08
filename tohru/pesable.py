"""Códigos "pesables": los que cargan PLU y peso en sus dígitos.

Formato clásico de báscula etiquetadora:

* 13 dígitos (EAN-13): ``[prefijo 2][PLU 5][peso 5][verificador]``
* 12 dígitos (UPC-A):  ``[prefijo 1][PLU 5][peso 5][verificador]``

El peso va en **centésimas de kilo** (``01250`` = 12,50 kg). Los códigos de
identidad (prefijos 07/08) no cargan peso y se rechazan a propósito: si los
decodificaras inventarías pesos fantasma.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ean13 import solo_digitos
from .identidad import PREFIJOS_IDENTIDAD


@dataclass(frozen=True)
class Pesable:
    """Resultado de decodificar un código con peso embebido."""

    plu: int
    peso_kg: float
    prefijo: str


def decodificar(codigo: str | None, centesimas: bool = True) -> Pesable | None:
    """Extrae PLU y peso de un código pesable.

    Devuelve ``None`` si el código no tiene 12 o 13 dígitos, si es de
    identidad, si el PLU es 0 o si los dígitos no son numéricos. Con
    ``centesimas=False`` el peso se interpreta en gramos (milésimas de kilo).

    >>> decodificar("2000023012507").peso_kg
    12.5
    """
    ean = solo_digitos(codigo)
    if len(ean) == 13:
        if ean[:2] in PREFIJOS_IDENTIDAD:
            return None
        prefijo, plu_s, peso_s = ean[:2], ean[2:7], ean[7:12]
    elif len(ean) == 12:
        if ean[0] in ("7", "8"):  # identidad con el 0 inicial mutilado
            return None
        prefijo, plu_s, peso_s = ean[:1], ean[1:6], ean[6:11]
    else:
        return None
    try:
        plu = int(plu_s)
        peso_int = int(peso_s)
    except ValueError:
        return None
    if plu <= 0:
        return None
    return Pesable(plu=plu, peso_kg=peso_int / (100.0 if centesimas else 1000.0), prefijo=prefijo)


def barcode_pesable(prefijo: str, plu: int, peso_kg: float, centesimas: bool = True) -> str:
    """Compone el EAN-13 pesable clásico (para etiquetas que sí cargan el peso).

    Redondea el peso a la resolución elegida. Ojo: dos paquetes del mismo
    producto y peso comparten código; si necesitas identidad por paquete usa
    :mod:`tohru.identidad`.
    """
    from .ean13 import completar

    if len(prefijo) != 2 or not prefijo.isdigit():
        raise ValueError(f"el prefijo debe ser de 2 dígitos, llegó {prefijo!r}")
    if prefijo in PREFIJOS_IDENTIDAD:
        raise ValueError(f"el prefijo {prefijo} está reservado para códigos de identidad")
    if not 1 <= plu <= 99_999:
        raise ValueError(f"PLU fuera de rango 1..99999: {plu}")
    factor = 100 if centesimas else 1000
    peso_int = round(peso_kg * factor)
    if not 0 <= peso_int <= 99_999:
        raise ValueError(f"peso fuera de rango para 5 dígitos: {peso_kg} kg")
    return completar(f"{prefijo}{plu:05d}{peso_int:05d}")
