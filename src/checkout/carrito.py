"""Carrito y orden como máquina de estados (RF-07, RF-08, RF-10).

Estados: VACIO -> CON_PRODUCTOS -> DATOS_CLIENTE -> RESUMEN -> COMPLETADO -> VACIO
"""
from enum import Enum

from .catalogo import obtener_producto
from .precios import calcular_resumen
from .validacion import validar_cliente


class Estado(str, Enum):
    VACIO = "VACIO"
    CON_PRODUCTOS = "CON_PRODUCTOS"
    DATOS_CLIENTE = "DATOS_CLIENTE"
    RESUMEN = "RESUMEN"
    COMPLETADO = "COMPLETADO"


class TransicionInvalida(Exception):
    """Se lanza cuando una acción no está permitida en el estado actual."""


class SesionExpirada(Exception):
    """Se lanza cuando se intenta usar el carrito sin sesión válida."""


class Carrito:
    def __init__(self):
        self.estado = Estado.VACIO
        self.productos = []          # ids en el orden en que se agregaron
        self.cliente = None
        self.resumen = None
        self.sesion_activa = True
        self.ordenes_confirmadas = []
        self._version = 0            # cambia cada vez que cambia el contenido
        self._version_resumen = None

    # ---- utilidades ----
    def _exigir(self, *permitidos):
        if not self.sesion_activa:
            raise SesionExpirada("You can only access this page when you are logged in")
        if self.estado not in permitidos:
            raise TransicionInvalida(f"Acción no permitida en estado {self.estado.value}")

    def expirar_sesion(self):
        self.sesion_activa = False

    # ---- T1, T2: agregar ----
    def agregar(self, id_producto):
        self._exigir(Estado.VACIO, Estado.CON_PRODUCTOS, Estado.RESUMEN)
        producto = obtener_producto(id_producto)        # TI-5: id inexistente
        if producto.id in self.productos:
            raise ValueError(f"{producto.nombre} ya está en el carrito")
        self.productos.append(producto.id)
        self._version += 1
        if self.estado == Estado.VACIO:
            self.estado = Estado.CON_PRODUCTOS

    # ---- T2, T3: quitar ----
    def quitar(self, id_producto):
        self._exigir(Estado.CON_PRODUCTOS, Estado.RESUMEN)
        producto = obtener_producto(id_producto)
        if producto.id not in self.productos:
            raise ValueError(f"{producto.nombre} no está en el carrito")
        self.productos.remove(producto.id)
        self._version += 1
        if not self.productos and self.estado == Estado.CON_PRODUCTOS:
            self.estado = Estado.VACIO

    # ---- T4 / TI-1 ----
    def iniciar_checkout(self):
        if self.estado == Estado.VACIO and self.sesion_activa:
            raise TransicionInvalida("No se puede iniciar el checkout con el carrito vacío")
        self._exigir(Estado.CON_PRODUCTOS)
        self.estado = Estado.DATOS_CLIENTE

    # ---- T6 / T10 ----
    def enviar_datos(self, nombre, apellido, codigo_postal):
        self._exigir(Estado.DATOS_CLIENTE)
        self.cliente = validar_cliente(nombre, apellido, codigo_postal)   # si falla, se queda en DATOS_CLIENTE
        self.resumen = self._calcular()
        self._version_resumen = self._version
        self.estado = Estado.RESUMEN

    # ---- T5 / T7 ----
    def cancelar(self):
        self._exigir(Estado.DATOS_CLIENTE, Estado.RESUMEN)
        self.estado = Estado.CON_PRODUCTOS if self.productos else Estado.VACIO

    # ---- T8 / TI-2 / TI-3 ----
    def finalizar(self):
        self._exigir(Estado.RESUMEN)
        if self._version != self._version_resumen:
            # TI-3: el carrito cambió después de mostrar el resumen -> se recalcula y no se confirma
            self.resumen = self._calcular()
            self._version_resumen = self._version
            raise TransicionInvalida("El carrito cambió; revise el resumen actualizado antes de confirmar")
        self.ordenes_confirmadas.append({"productos": list(self.productos), "resumen": self.resumen})
        self.productos.clear()
        self.estado = Estado.COMPLETADO

    # ---- T9 ----
    def volver_inicio(self):
        self._exigir(Estado.COMPLETADO)
        self.cliente = None
        self.resumen = None
        self.estado = Estado.VACIO

    def _calcular(self):
        return calcular_resumen(obtener_producto(i).precio for i in self.productos)
