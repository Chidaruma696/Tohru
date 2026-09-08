"""Tohru: códigos de barras de báscula (EAN-13) sin dependencias.

* :mod:`tohru.ean13` — dígito verificador y validación.
* :mod:`tohru.identidad` — códigos que identifican al paquete (el peso vive en tu base).
* :mod:`tohru.pesable` — códigos clásicos que cargan PLU y peso en los dígitos.
* :mod:`tohru.lector` — tolerancia a lectores que mutilan dígitos y elección de la fila viva.
"""

from .ean13 import completar, digito_verificador, es_valido, solo_digitos
from .identidad import (
    CAPACIDAD,
    PREFIJO_CAJA,
    PREFIJO_PESADA,
    PREFIJOS_IDENTIDAD,
    EstadoSecuencia,
    barcode_identidad,
    descomponer,
    es_identidad,
    estado_secuencia,
)
from .lector import VIVOS_CAJA, VIVOS_PESADA, preferir_viva, variantes
from .pesable import Pesable, barcode_pesable, decodificar

__version__ = "0.1.0"

__all__ = [
    "CAPACIDAD",
    "PREFIJO_CAJA",
    "PREFIJO_PESADA",
    "PREFIJOS_IDENTIDAD",
    "VIVOS_CAJA",
    "VIVOS_PESADA",
    "EstadoSecuencia",
    "Pesable",
    "barcode_identidad",
    "barcode_pesable",
    "completar",
    "decodificar",
    "descomponer",
    "digito_verificador",
    "es_identidad",
    "es_valido",
    "estado_secuencia",
    "preferir_viva",
    "solo_digitos",
    "variantes",
]
