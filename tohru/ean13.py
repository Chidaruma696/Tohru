"""EAN-13: dígito verificador y validación.

Todo trabaja sobre cadenas de dígitos; nunca se convierte a entero para no
perder los ceros a la izquierda, que en un código de barras significan.
"""

from __future__ import annotations

import re

_SOLO_DIGITOS = re.compile(r"\D")


def solo_digitos(texto: str | None) -> str:
    """Quita todo lo que no sea dígito (espacios, guiones, lo que meta un lector)."""
    return _SOLO_DIGITOS.sub("", texto or "")


def digito_verificador(base12: str) -> str:
    """Dígito verificador EAN-13 de una base de 12 dígitos.

    Las posiciones impares (contando desde la izquierda, 1-indexadas) pesan 1
    y las pares pesan 3; el verificador completa la suma al múltiplo de 10.

    >>> digito_verificador("750105922482")
    '7'
    """
    if len(base12) != 12 or not base12.isdigit():
        raise ValueError(f"se esperaban 12 dígitos, llegó {base12!r}")
    suma = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base12))
    return str((10 - suma % 10) % 10)


def completar(base12: str) -> str:
    """Devuelve el EAN-13 completo (base + verificador)."""
    return base12 + digito_verificador(base12)


def es_valido(codigo: str | None) -> bool:
    """True si el texto es un EAN-13 de 13 dígitos con verificador correcto."""
    ean = solo_digitos(codigo)
    return len(ean) == 13 and digito_verificador(ean[:12]) == ean[12]
