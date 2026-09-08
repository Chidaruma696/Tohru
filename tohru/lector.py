"""Tolerancia a lectores de código de barras.

Un lector de mano no siempre entrega los 13 dígitos: hay modelos que se
comen el ``0`` inicial (leen el EAN-13 como UPC-A), otros omiten el dígito
verificador, y algunos las dos cosas. :func:`variantes` genera todas las
formas en que ese código puede estar guardado para buscarlas de una vez;
:func:`preferir_viva` elige bien cuando la búsqueda devuelve gemelas.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from .ean13 import digito_verificador

VIVOS_PESADA = ("disponible", "en_caja")
"""Estados en los que una pesada sigue siendo escaneable o vendible."""

VIVOS_CAJA = ("abierta", "cerrada")
"""Estados en los que una caja sigue viva."""


def variantes(codigo: str | None) -> list[str]:
    """Todas las formas en que un lector pudo haber entregado el código.

    * tal cual y sin espacios;
    * 12 dígitos: con verificador calculado, y con ``0`` delante (UPC-A → EAN-13);
    * 13 dígitos: sin verificador, y sin el ``0`` inicial si lo tiene;
    * 11 dígitos: reponiendo ``0`` inicial y verificador (el lector se comió ambos).

    Sin duplicados y en orden de aparición.

    >>> variantes("0750105922482")
    ['0750105922482', '075010592248', '750105922482']
    """
    if not codigo:
        return []
    bruto = codigo.strip()
    if not bruto:
        return []
    limpio = re.sub(r"\s+", "", bruto)
    cands = [bruto] if bruto == limpio else [bruto, limpio]

    if re.fullmatch(r"\d{12}", limpio):
        cands.append(limpio + digito_verificador(limpio))
        cands.append("0" + limpio)
    elif re.fullmatch(r"\d{13}", limpio):
        cands.append(limpio[:12])
        if limpio.startswith("0"):
            cands.append(limpio[1:])
    elif re.fullmatch(r"\d{11}", limpio):
        con_cero = "0" + limpio
        cands.append(con_cero + digito_verificador(con_cero))
        cands.append(con_cero)

    salida: list[str] = []
    for c in cands:
        if c and c not in salida:
            salida.append(c)
    return salida


def preferir_viva(
    filas: Iterable[Mapping[str, Any]],
    vivos: Iterable[str] = VIVOS_PESADA,
    campo: str = "estado",
) -> Mapping[str, Any] | None:
    """Entre varias filas que coinciden con las variantes de un código, la viva gana.

    En una base pueden convivir gemelas del mismo código con y sin cero
    inicial (una viva, otra anulada). Elegir "la primera" al azar hace que la
    muerta secuestre el escaneo. Devuelve la primera viva, o la primera fila
    si ninguna lo está, o ``None`` si no hay filas.
    """
    lista = list(filas)
    if not lista:
        return None
    vivos_set = set(vivos)
    for fila in lista:
        if (fila.get(campo) or "") in vivos_set:
            return fila
    return lista[0]
