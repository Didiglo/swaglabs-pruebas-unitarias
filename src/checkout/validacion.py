"""Validación del formulario "Your Information" del checkout (RF-02, RF-03, RF-04, RF-09)."""
from dataclasses import dataclass

LONG_MIN_NOMBRE, LONG_MAX_NOMBRE = 1, 50
LONG_MIN_POSTAL, LONG_MAX_POSTAL = 3, 10


class ErrorValidacion(Exception):
    """Error de un campo del formulario. `campo` dice cuál falló."""

    def __init__(self, campo: str, mensaje: str):
        super().__init__(mensaje)
        self.campo = campo
        self.mensaje = mensaje


@dataclass(frozen=True)
class DatosCliente:
    nombre: str
    apellido: str
    codigo_postal: str


def _validar_nombre(valor, campo: str, etiqueta: str) -> str:
    texto = (valor or "").strip()
    if not texto:
        raise ErrorValidacion(campo, f"Error: {etiqueta} is required")
    if len(texto) > LONG_MAX_NOMBRE:
        raise ErrorValidacion(campo, f"Error: {etiqueta} must be at most {LONG_MAX_NOMBRE} characters")
    return texto


def _validar_postal(valor) -> str:
    texto = (valor or "").strip()
    if not texto:
        raise ErrorValidacion("codigo_postal", "Error: Postal Code is required")
    if not (LONG_MIN_POSTAL <= len(texto) <= LONG_MAX_POSTAL):
        raise ErrorValidacion(
            "codigo_postal",
            f"Error: Postal Code must be {LONG_MIN_POSTAL} to {LONG_MAX_POSTAL} characters",
        )
    if not texto.isascii() or not texto.isalnum():
        raise ErrorValidacion("codigo_postal", "Error: Postal Code must contain only letters and digits")
    return texto


def validar_cliente(nombre, apellido, codigo_postal) -> DatosCliente:
    """Valida los tres campos en el orden de la pantalla y devuelve los datos recortados.

    Si hay más de un campo inválido se informa solo el primero (tabla de decisión T2).
    """
    return DatosCliente(
        nombre=_validar_nombre(nombre, "nombre", "First Name"),
        apellido=_validar_nombre(apellido, "apellido", "Last Name"),
        codigo_postal=_validar_postal(codigo_postal),
    )
