"""CU-01 Ingresar datos del cliente en el checkout.

Cubre RF-02 (First Name), RF-03 (Last Name), RF-04 (Postal Code) y RF-09
(el error identifica solo el campo que falló). Las pruebas siguen la partición
de equivalencia, los valores límite y la tabla de decisión T2 del Laboratorio 3.
"""
import pytest

from checkout.validacion import ErrorValidacion, validar_cliente

N49 = "Diana" * 9 + "Dian"
N50 = "Diana" * 10
N51 = N50 + "D"


def test_datos_validos_se_aceptan_y_se_recortan():
    """Camino feliz (CP-01, T2-R1): con los tres campos válidos se devuelven los datos sin espacios extra."""
    datos = validar_cliente("  Diana ", "Rosario", " 10101 ")
    assert (datos.nombre, datos.apellido, datos.codigo_postal) == ("Diana", "Rosario", "10101")


@pytest.mark.parametrize("nombre", ["D", "Di", N49, N50], ids=["len1", "len2", "len49", "len50"])
def test_nombre_en_limites_validos(nombre):
    """Valores límite de First Name (CP-08): 1, 2, 49 y 50 caracteres son válidos."""
    assert validar_cliente(nombre, "Rosario", "10101").nombre == nombre


@pytest.mark.parametrize("nombre, mensaje", [
    ("", "Error: First Name is required"),            # CI-N1, límite 0 (CP-02)
    ("   ", "Error: First Name is required"),         # CI-N2, solo espacios (CP-03)
    (None, "Error: First Name is required"),          # campo ausente
    (N51, "Error: First Name must be at most 50 characters"),  # CI-N3, límite 51 (CP-09)
], ids=["vacio", "solo_espacios", "none", "len51"])
def test_nombre_invalido_se_rechaza(nombre, mensaje):
    """Clases inválidas de First Name: el error nombra el campo y trae el mensaje esperado."""
    with pytest.raises(ErrorValidacion) as e:
        validar_cliente(nombre, "Rosario", "10101")
    assert e.value.campo == "nombre"
    assert e.value.mensaje == mensaje


@pytest.mark.parametrize("apellido", ["", N51], ids=["vacio", "len51"])
def test_apellido_invalido_se_rechaza(apellido):
    """Last Name tiene las mismas reglas que First Name (CP-15)."""
    with pytest.raises(ErrorValidacion) as e:
        validar_cliente("Diana", apellido, "10101")
    assert e.value.campo == "apellido"


@pytest.mark.parametrize("postal", ["101", "1010", "101010101", "1010101010", "AB12c"],
                         ids=["len3", "len4", "len9", "len10", "alfanumerico"])
def test_codigo_postal_valido(postal):
    """Valores límite del código postal (CP-10): 3, 4, 9 y 10 caracteres, y mezcla de letras y dígitos."""
    assert validar_cliente("Diana", "Rosario", postal).codigo_postal == postal


@pytest.mark.parametrize("postal, mensaje", [
    ("", "Error: Postal Code is required"),                                 # CI-Z1 (CP-16)
    ("10", "Error: Postal Code must be 3 to 10 characters"),                # límite 2 (CP-11)
    ("10101010101", "Error: Postal Code must be 3 to 10 characters"),       # límite 11 (CP-11)
    ("ABC-!@#", "Error: Postal Code must contain only letters and digits"), # CI-Z2 (CP-04)
    ("1010ñ", "Error: Postal Code must contain only letters and digits"),   # carácter no ASCII
], ids=["vacio", "len2", "len11", "simbolos", "no_ascii"])
def test_codigo_postal_invalido(postal, mensaje):
    """Clases inválidas del código postal: vacío, fuera de longitud y con símbolos."""
    with pytest.raises(ErrorValidacion) as e:
        validar_cliente("Diana", "Rosario", postal)
    assert e.value.campo == "codigo_postal"
    assert e.value.mensaje == mensaje


@pytest.mark.parametrize("nombre, apellido, postal, campo", [
    ("Diana", "Rosario", "", "codigo_postal"),   # T2-R2
    ("Diana", "", "10101", "apellido"),          # T2-R3
    ("Diana", "", "", "apellido"),               # T2-R3 (Postal Code indiferente)
    ("", "Rosario", "10101", "nombre"),          # T2-R4
    ("", "", "", "nombre"),                      # T2-R4 (los otros dos indiferentes)
], ids=["R2", "R3", "R3_postal_indif", "R4", "R4_todo_vacio"])
def test_tabla_decision_t2_informa_el_primer_campo_invalido(nombre, apellido, postal, campo):
    """Tabla de decisión T2: con varios campos inválidos se informa el primero en el orden de la pantalla."""
    with pytest.raises(ErrorValidacion) as e:
        validar_cliente(nombre, apellido, postal)
    assert e.value.campo == campo
