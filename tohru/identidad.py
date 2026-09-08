"""Barcode de identidad: el código identifica al paquete, no carga su peso.

Formato EAN-13: ``[prefijo 2][PLU 5][secuencia 5][verificador]``.

Dos paquetes del mismo producto y el mismo peso jamás comparten código,
porque la secuencia es única. El peso vive en tu base de datos, no en los
dígitos; por eso :func:`tohru.pesable.decodificar` rechaza estos prefijos a
propósito.

La secuencia se reserva **antes** de guardar la fila: pides el siguiente
número a tu base (o a un contador) y guardas la fila ya con su código. Así no
existe un estado intermedio "sin código" que un lector no pueda encontrar.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ean13 import completar

PREFIJO_PESADA = "08"
"""Prefijo por defecto para etiquetas de una pesada individual."""

PREFIJO_CAJA = "07"
"""Prefijo por defecto para cajas que agrupan pesadas."""

PREFIJOS_IDENTIDAD = (PREFIJO_PESADA, PREFIJO_CAJA)

CAPACIDAD = 100_000
"""Cuántas secuencias distintas caben en los 5 dígitos: de 0 a 99 999."""

MAX_PLU = 99_999


def barcode_identidad(prefijo: str, plu: int | None, secuencia: int) -> str:
    """Compone el EAN-13 de identidad.

    ``prefijo`` son dos dígitos; ``plu`` el número del producto en la báscula
    (``None`` o 0 se codifica como ``00000``); ``secuencia`` un entero no
    negativo que se toma módulo :data:`CAPACIDAD`.

    >>> barcode_identidad("08", 90050, 49006)
    '0890050490063'
    """
    if len(prefijo) != 2 or not prefijo.isdigit():
        raise ValueError(f"el prefijo debe ser de 2 dígitos, llegó {prefijo!r}")
    plu_n = int(plu or 0)
    if not 0 <= plu_n <= MAX_PLU:
        raise ValueError(f"PLU fuera de rango 0..{MAX_PLU}: {plu_n}")
    if secuencia < 0:
        raise ValueError(f"la secuencia no puede ser negativa: {secuencia}")
    base = f"{prefijo}{plu_n:05d}{secuencia % CAPACIDAD:05d}"
    return completar(base)


def descomponer(codigo: str) -> tuple[str, int, int] | None:
    """``(prefijo, plu, secuencia)`` de un código de identidad, o ``None`` si
    no es uno (prefijo desconocido, longitud o verificador incorrectos).

    Acepta la variante de 12 dígitos a la que un lector le comió el ``0``
    inicial.
    """
    from .ean13 import es_valido, solo_digitos

    ean = solo_digitos(codigo)
    if len(ean) == 12 and ean[0] in ("7", "8"):
        ean = "0" + ean
    if len(ean) != 13 or ean[:2] not in PREFIJOS_IDENTIDAD or not es_valido(ean):
        return None
    return ean[:2], int(ean[2:7]), int(ean[7:12])


def es_identidad(codigo: str) -> bool:
    """True si el código es de identidad (prefijos 07/08), con o sin el 0 inicial."""
    return descomponer(codigo) is not None


@dataclass(frozen=True)
class EstadoSecuencia:
    """Cuánto queda antes de que la secuencia dé la vuelta."""

    ultima: int
    capacidad: int = CAPACIDAD

    @property
    def usadas(self) -> int:
        return min(self.ultima + 1, self.capacidad)

    @property
    def restantes(self) -> int:
        return max(self.capacidad - self.ultima - 1, 0)

    @property
    def dio_la_vuelta(self) -> bool:
        return self.ultima >= self.capacidad - 1

    def meses_restantes(self, ritmo_mensual: float) -> float | None:
        """Meses que faltan al ritmo dado, o ``None`` si el ritmo es 0."""
        if ritmo_mensual <= 0:
            return None
        return self.restantes / ritmo_mensual


def estado_secuencia(ultima_secuencia: int, capacidad: int = CAPACIDAD) -> EstadoSecuencia:
    """Resume el uso del espacio de secuencias a partir de la última emitida.

    Úsalo para mostrar un aviso con tiempo: cuando la vuelta llega, dos
    paquetes vivos pueden compartir código y el esquema deja de identificar.
    Antes de eso conviene cambiar de prefijo (``07``/``08`` son solo el
    default: cualquier par de dígitos que no choque con tus GTIN vale).
    """
    return EstadoSecuencia(ultima=ultima_secuencia, capacidad=capacidad)
