"""CU-02 Calcular el resumen de la orden.

Cubre RF-05 (10 % de descuento a partir de 100.00) y RF-06 (8 % de impuesto
sobre el monto descontado, redondeado a centavos). Incluye el límite 100.00,
que en la interfaz de Swag Labs no se puede alcanzar (ambigüedad A-06 del Lab 3)
pero que aquí sí se prueba porque la función recibe los precios directamente.
"""
from decimal import Decimal as D

import pytest

from checkout.precios import calcular_resumen


@pytest.mark.parametrize("precios, subtotal, descuento, impuesto, total", [
    (["29.99"], "29.99", "0.00", "2.40", "32.39"),                                   # CP-01
    (["9.99", "15.99", "7.99", "15.99", "49.99"], "99.95", "0.00", "8.00", "107.95"),  # CP-12
    (["99.99"], "99.99", "0.00", "8.00", "107.99"),                                   # justo debajo
    (["100.00"], "100.00", "10.00", "7.20", "97.20"),                                 # en el límite
    (["100.01"], "100.01", "10.00", "7.20", "97.21"),                                 # justo encima
    (["15.99", "7.99", "29.99", "49.99"], "103.96", "10.40", "7.48", "101.04"),        # CP-13
], ids=["un_producto", "cp12_99.95", "99.99", "100.00", "100.01", "cp13_103.96"])
def test_resumen_alrededor_del_limite_de_descuento(precios, subtotal, descuento, impuesto, total):
    """Valores límite del descuento: 99.99 no lo recibe, 100.00 y 100.01 sí."""
    r = calcular_resumen(D(p) for p in precios)
    assert (r.subtotal, r.descuento, r.impuesto, r.total) == (D(subtotal), D(descuento), D(impuesto), D(total))


def test_total_es_subtotal_menos_descuento_mas_impuesto():
    """Coherencia interna: el total siempre cuadra con las otras tres líneas."""
    r = calcular_resumen([D("49.99"), D("29.99"), D("29.99")])
    assert r.total == r.subtotal - r.descuento + r.impuesto


def test_redondeo_mitad_hacia_arriba():
    """El impuesto se redondea a centavos con mitad hacia arriba (0.625 -> 0.63), no se trunca."""
    r = calcular_resumen([D("7.8125")])          # 7.8125 -> subtotal 7.81 ; 8 % de 7.81 = 0.6248
    assert r.impuesto == D("0.62")
    r = calcular_resumen([D("7.8125"), D("0.0025")])  # subtotal 7.815 -> 7.82 ; 8 % = 0.6256 -> 0.63
    assert r.subtotal == D("7.82") and r.impuesto == D("0.63")


def test_orden_sin_productos_se_rechaza():
    """Clase inválida: no se calcula un resumen para una orden vacía (RF-07)."""
    with pytest.raises(ValueError, match="no tiene productos"):
        calcular_resumen([])


def test_precio_negativo_se_rechaza():
    """Clase inválida: un precio negativo es un error de datos, no un descuento."""
    with pytest.raises(ValueError, match="negativo"):
        calcular_resumen([D("10.00"), D("-5.00")])
