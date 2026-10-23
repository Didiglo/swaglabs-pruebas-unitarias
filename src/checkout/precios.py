"""Cálculo del resumen de la orden (RF-05, RF-06)."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

UMBRAL_DESCUENTO = Decimal("100.00")
TASA_DESCUENTO = Decimal("0.10")
TASA_IMPUESTO = Decimal("0.08")
CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class Resumen:
    subtotal: Decimal
    descuento: Decimal
    impuesto: Decimal
    total: Decimal


def redondear(valor: Decimal) -> Decimal:
    """Redondeo a centavos, mitad hacia arriba (29.99 x 8 % = 2.3992 -> 2.40)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def calcular_resumen(precios: Iterable[Decimal]) -> Resumen:
    """Calcula subtotal, descuento, impuesto y total.

    - Descuento del 10 % si el subtotal es de 100.00 o más ("a partir de").
    - Impuesto del 8 % sobre el monto ya descontado.
    """
    lista = [Decimal(p) for p in precios]
    if not lista:
        raise ValueError("La orden no tiene productos")
    if any(p < 0 for p in lista):
        raise ValueError("Un precio no puede ser negativo")
    subtotal = redondear(sum(lista, Decimal("0")))
    descuento = redondear(subtotal * TASA_DESCUENTO) if subtotal >= UMBRAL_DESCUENTO else Decimal("0.00")
    base = subtotal - descuento
    impuesto = redondear(base * TASA_IMPUESTO)
    return Resumen(subtotal, descuento, impuesto, base + impuesto)
