"""Catálogo de productos de Swag Labs (RF-01)."""
from dataclasses import dataclass
from decimal import Decimal


class ProductoNoEncontrado(Exception):
    """Se lanza cuando se pide un id que no existe en el catálogo."""


@dataclass(frozen=True)
class Producto:
    id: int
    nombre: str
    precio: Decimal


CATALOGO = {
    0: Producto(0, "Sauce Labs Bike Light", Decimal("9.99")),
    1: Producto(1, "Sauce Labs Bolt T-Shirt", Decimal("15.99")),
    2: Producto(2, "Sauce Labs Onesie", Decimal("7.99")),
    3: Producto(3, "Test.allTheThings() T-Shirt (Red)", Decimal("15.99")),
    4: Producto(4, "Sauce Labs Backpack", Decimal("29.99")),
    5: Producto(5, "Sauce Labs Fleece Jacket", Decimal("49.99")),
}


def obtener_producto(id_producto) -> Producto:
    """Devuelve el producto con ese id.

    Acepta un entero o un texto con dígitos (como llega en ?id=3 de la URL).
    Cualquier otro valor (negativo, mayor que 5, no numérico, None) lanza
    ProductoNoEncontrado.
    """
    if isinstance(id_producto, bool):
        raise ProductoNoEncontrado(id_producto)
    if isinstance(id_producto, str):
        texto = id_producto.strip()
        if not texto.lstrip("-").isdigit():
            raise ProductoNoEncontrado(id_producto)
        id_producto = int(texto)
    if not isinstance(id_producto, int) or id_producto not in CATALOGO:
        raise ProductoNoEncontrado(id_producto)
    return CATALOGO[id_producto]
