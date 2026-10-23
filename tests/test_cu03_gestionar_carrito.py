"""CU-03 Gestionar el carrito y confirmar la orden.

Cubre RF-01 (solo productos del catálogo), RF-07 (no checkout con carrito vacío),
RF-08 (Finish confirma lo que se mostró, sin reconfirmar) y RF-10 (sesión válida).
Sigue el diagrama de estados del Laboratorio 3: transiciones válidas T1–T10 e
inválidas TI-1 a TI-5.
"""
from decimal import Decimal as D

import pytest

from checkout.carrito import Carrito, Estado, SesionExpirada, TransicionInvalida
from checkout.catalogo import ProductoNoEncontrado, obtener_producto
from checkout.validacion import ErrorValidacion


@pytest.fixture
def carrito():
    return Carrito()


def llevar_a_resumen(c, *ids):
    for i in ids:
        c.agregar(i)
    c.iniciar_checkout()
    c.enviar_datos("Diana", "Rosario", "10101")


# ---------- Catálogo (RF-01, partición de equivalencia y límites del id) ----------

@pytest.mark.parametrize("id_producto, nombre", [
    (0, "Sauce Labs Bike Light"), (3, "Test.allTheThings() T-Shirt (Red)"),
    (5, "Sauce Labs Fleece Jacket"), ("4", "Sauce Labs Backpack"),
], ids=["limite_0", "representante_3", "limite_5", "texto_4"])
def test_producto_existente(id_producto, nombre):
    """CP-06: los ids 0 a 5 existen (también si llegan como texto desde la URL)."""
    assert obtener_producto(id_producto).nombre == nombre


@pytest.mark.parametrize("id_producto", [-1, 6, 99, "abc", None, "", 2.5, True],
                         ids=["-1", "6", "99", "abc", "ausente", "vacio", "decimal", "bool"])
def test_producto_inexistente(id_producto):
    """CP-05 y CP-07: fuera de 0..5, no numérico o ausente -> ProductoNoEncontrado."""
    with pytest.raises(ProductoNoEncontrado):
        obtener_producto(id_producto)


# ---------- Transiciones válidas ----------

def test_ciclo_completo_con_cancel_y_retorno(carrito):
    """CP-17: T1, T4, T6, T7 (Cancel), T4, T6, T8 (Finish) y T9 (Back Home)."""
    carrito.agregar(2)
    assert carrito.estado == Estado.CON_PRODUCTOS
    carrito.iniciar_checkout()
    assert carrito.estado == Estado.DATOS_CLIENTE
    carrito.enviar_datos("Diana", "Rosario", "10101")
    assert carrito.estado == Estado.RESUMEN
    carrito.cancelar()
    assert carrito.estado == Estado.CON_PRODUCTOS and carrito.productos == [2]
    carrito.iniciar_checkout()
    carrito.enviar_datos("Diana", "Rosario", "10101")
    carrito.finalizar()
    assert carrito.estado == Estado.COMPLETADO
    assert carrito.ordenes_confirmadas[0]["resumen"].total == D("8.63")
    carrito.volver_inicio()
    assert carrito.estado == Estado.VACIO and carrito.productos == []


def test_quitar_el_ultimo_producto_vuelve_a_vacio(carrito):
    """T2 y T3: quitar con más de un producto deja CON_PRODUCTOS; quitar el último deja VACIO."""
    carrito.agregar(0)
    carrito.agregar(1)
    carrito.quitar(0)
    assert carrito.estado == Estado.CON_PRODUCTOS
    carrito.quitar(1)
    assert carrito.estado == Estado.VACIO


def test_cancel_en_datos_cliente_vuelve_al_carrito(carrito):
    """T5: Cancel en el paso 1 vuelve a CON_PRODUCTOS sin perder productos."""
    carrito.agregar(4)
    carrito.iniciar_checkout()
    carrito.cancelar()
    assert carrito.estado == Estado.CON_PRODUCTOS and carrito.productos == [4]


def test_datos_invalidos_no_avanzan(carrito):
    """T10: Continue con datos inválidos deja el carrito en DATOS_CLIENTE."""
    carrito.agregar(4)
    carrito.iniciar_checkout()
    with pytest.raises(ErrorValidacion):
        carrito.enviar_datos("", "Rosario", "10101")
    assert carrito.estado == Estado.DATOS_CLIENTE


# ---------- Transiciones inválidas ----------

def test_checkout_con_carrito_vacio_se_impide(carrito):
    """TI-1 (CP-14): no se puede iniciar el checkout sin productos."""
    with pytest.raises(TransicionInvalida, match="vacío"):
        carrito.iniciar_checkout()
    assert carrito.estado == Estado.VACIO


def test_orden_completada_no_se_puede_reconfirmar(carrito):
    """TI-2 (CP-18): después de Finish no se puede volver a confirmar la orden."""
    llevar_a_resumen(carrito, 2)
    carrito.finalizar()
    with pytest.raises(TransicionInvalida):
        carrito.finalizar()
    assert len(carrito.ordenes_confirmadas) == 1


def test_finish_con_carrito_cambiado_no_confirma(carrito):
    """TI-3 (CP-19): si el carrito cambia después del resumen, Finish no confirma y recalcula."""
    llevar_a_resumen(carrito, 0)                 # Bike Light: total 10.79
    assert carrito.resumen.total == D("10.79")
    carrito.quitar(0)                            # "otra pestaña"
    carrito.agregar(2)                           # Onesie
    with pytest.raises(TransicionInvalida, match="cambió"):
        carrito.finalizar()
    assert carrito.ordenes_confirmadas == []
    assert carrito.resumen.total == D("8.63")    # resumen actualizado
    carrito.finalizar()                          # ahora sí confirma lo que se mostró
    assert carrito.ordenes_confirmadas[0]["productos"] == [2]


def test_add_to_cart_con_sesion_expirada(carrito):
    """TI-4 (CP-20): sin sesión válida el carrito no cambia."""
    carrito.expirar_sesion()
    with pytest.raises(SesionExpirada):
        carrito.agregar(1)
    assert carrito.productos == []


def test_agregar_id_inexistente_no_cambia_el_carrito(carrito):
    """TI-5: agregar un id que no existe deja el carrito igual."""
    with pytest.raises(ProductoNoEncontrado):
        carrito.agregar(6)
    assert carrito.estado == Estado.VACIO and carrito.productos == []


def test_producto_repetido_y_quitar_lo_que_no_esta(carrito):
    """QTY es siempre 1 en Swag Labs: no se agrega dos veces ni se quita lo que no está."""
    carrito.agregar(1)
    with pytest.raises(ValueError, match="ya está"):
        carrito.agregar(1)
    with pytest.raises(ValueError, match="no está"):
        carrito.quitar(3)


@pytest.mark.parametrize("accion", ["enviar_datos", "cancelar", "finalizar", "volver_inicio"])
def test_acciones_fuera_de_orden_desde_vacio(carrito, accion):
    """Ninguna acción del checkout está permitida si el carrito está VACIO."""
    args = ("Diana", "Rosario", "10101") if accion == "enviar_datos" else ()
    with pytest.raises(TransicionInvalida):
        getattr(carrito, accion)(*args)
