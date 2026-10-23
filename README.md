# Pruebas unitarias del checkout de Swag Labs

**TI3-312 Aseguramiento de la Calidad del Software · UNIBE · Actividad 6**
Estudiante: Diana Rosario Batista (25-1312) · Docente: Lorenzo Martínez

Este repositorio implementa las reglas de negocio del flujo de compra de
[Swag Labs](https://www.saucedemo.com/), la aplicación usada en los laboratorios 1 a 3,
y las cubre con **62 pruebas unitarias en pytest** para **tres casos de uso**.
Las reglas (RF-01 a RF-10) y los casos de prueba de referencia (CP-01 a CP-20)
vienen del Laboratorio 3.

Swag Labs es una aplicación de terceros y su código no está disponible, así que no se
le pueden hacer pruebas unitarias directamente. Por eso las reglas se escribieron
como un módulo de Python (`src/checkout`) y las pruebas se hacen sobre ese módulo.

## Cómo ejecutar las pruebas

Requisitos: Python 3.9 o superior.

```bash
git clone https://github.com/Didiglo/swaglabs-pruebas-unitarias.git
cd swaglabs-pruebas-unitarias
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python -m pytest                                    # corre las 62 pruebas
python -m pytest tests/test_cu01_validar_cliente.py # solo un caso de uso
python -m pytest --cov=checkout --cov-branch --cov-report=term-missing   # con cobertura
```

Resultado esperado: `62 passed` y 100 % de cobertura de líneas y de ramas.

## Estructura

```
src/checkout/
  catalogo.py     productos 0 a 5 y búsqueda por id               (RF-01)
  validacion.py   formulario "Your Information"                   (RF-02, RF-03, RF-04, RF-09)
  precios.py      subtotal, descuento, impuesto y total           (RF-05, RF-06)
  carrito.py      carrito y orden como máquina de estados         (RF-07, RF-08, RF-10)
tests/
  test_cu01_validar_cliente.py     CU-01  (26 pruebas)
  test_cu02_calcular_resumen.py    CU-02  (10 pruebas)
  test_cu03_gestionar_carrito.py   CU-03  (26 pruebas)
```

## Reglas de negocio

| ID | Regla |
|---|---|
| RF-01 | Solo existen los productos con id 0 a 5. |
| RF-02 | First Name obligatorio, 1 a 50 caracteres; se recortan los espacios. |
| RF-03 | Last Name, mismas reglas que First Name. |
| RF-04 | Postal Code obligatorio, alfanumérico, 3 a 10 caracteres. |
| RF-05 | 10 % de descuento a partir de 100.00 (100.00 incluido). |
| RF-06 | 8 % de impuesto sobre el monto ya descontado, redondeado a centavos (mitad hacia arriba). |
| RF-07 | No se puede iniciar el checkout con el carrito vacío. |
| RF-08 | Finish confirma exactamente lo que se mostró y una orden no se puede confirmar dos veces. |
| RF-09 | El error de validación identifica el campo que falló (el primero, en el orden de la pantalla). |
| RF-10 | Sin sesión válida no se puede modificar el carrito. |

## Casos de uso y sus pruebas

### CU-01 Ingresar datos del cliente en el checkout

**Actor:** comprador. **Flujo principal:** con productos en el carrito pulsa *Checkout*,
escribe nombre, apellido y código postal y pulsa *Continue*; el sistema valida y muestra el resumen.
**Flujos alternos:** algún campo vacío, fuera de longitud o con caracteres no permitidos → el
sistema muestra el error del primer campo inválido y no avanza.

| Prueba | Propósito | Técnica | Reglas / CP |
|---|---|---|---|
| `test_datos_validos_se_aceptan_y_se_recortan` | Camino feliz: datos válidos se aceptan y se guardan sin espacios extra. | Partición (clase válida) | RF-02–04 · CP-01 |
| `test_nombre_en_limites_validos` (×4) | 1, 2, 49 y 50 caracteres son válidos. | Valores límite | RF-02 · CP-08 |
| `test_nombre_invalido_se_rechaza` (×4) | Vacío, solo espacios, ausente y 51 caracteres se rechazan con el mensaje correcto. | Partición + límites | RF-02 · CP-02, 03, 09 |
| `test_apellido_invalido_se_rechaza` (×2) | Last Name vacío o de 51 caracteres se rechaza. | Partición | RF-03 · CP-15 |
| `test_codigo_postal_valido` (×5) | 3, 4, 9 y 10 caracteres y mezcla de letras/dígitos son válidos. | Valores límite | RF-04 · CP-10 |
| `test_codigo_postal_invalido` (×5) | Vacío, 2 y 11 caracteres, símbolos y caracteres no ASCII se rechazan. | Partición + límites | RF-04 · CP-04, 11, 16 |
| `test_tabla_decision_t2_informa_el_primer_campo_invalido` (×5) | Con varios campos inválidos se informa el primero. | Tabla de decisión T2 | RF-09 |

### CU-02 Calcular el resumen de la orden

**Actor:** sistema. **Flujo principal:** al pasar al *Overview* calcula subtotal, descuento,
impuesto y total a partir de los precios del carrito.
**Flujos alternos:** subtotal desde 100.00 → aplica descuento; orden vacía o precio negativo → error.

| Prueba | Propósito | Técnica | Reglas / CP |
|---|---|---|---|
| `test_resumen_alrededor_del_limite_de_descuento` (×6) | 99.95 y 99.99 no tienen descuento; 100.00, 100.01 y 103.96 sí. Verifica las cuatro líneas del resumen. | Valores límite | RF-05, RF-06 · CP-01, 12, 13 |
| `test_total_es_subtotal_menos_descuento_mas_impuesto` | El total siempre cuadra con las otras líneas. | Coherencia | RF-05, RF-06 |
| `test_redondeo_mitad_hacia_arriba` | Se redondea a centavos, no se trunca. | Valores límite | RF-06 |
| `test_orden_sin_productos_se_rechaza` | No se calcula un resumen vacío. | Partición (inválida) | RF-07 |
| `test_precio_negativo_se_rechaza` | Un precio negativo es un error de datos. | Partición (inválida) | — |

El límite exacto de 100.00 no se puede producir en la interfaz de Swag Labs con su catálogo
(ambigüedad A-06 del Lab 3). En la prueba unitaria sí se cubre porque la función recibe los precios.

### CU-03 Gestionar el carrito y confirmar la orden

**Actor:** comprador. **Flujo principal:** agrega productos, inicia el checkout, envía sus datos,
revisa el resumen y pulsa *Finish*; luego vuelve al inicio con el carrito vacío.
**Flujos alternos:** Cancel en el paso 1 o en el resumen; quitar productos; acciones no permitidas
(checkout vacío, reconfirmar, carrito cambiado, sesión expirada, producto inexistente).

| Prueba | Propósito | Técnica | Reglas / CP |
|---|---|---|---|
| `test_producto_existente` (×4) | ids 0, 3, 5 y "4" existen. | Partición + límites | RF-01 · CP-06 |
| `test_producto_inexistente` (×8) | -1, 6, 99, "abc", ausente, vacío, 2.5 y bool no existen. | Partición + límites | RF-01 · CP-05, 07 |
| `test_ciclo_completo_con_cancel_y_retorno` | Recorre T1, T4, T6, T7, T4, T6, T8, T9 y verifica el total 8.63. | Transición de estados | RF-08 · CP-17 |
| `test_quitar_el_ultimo_producto_vuelve_a_vacio` | T2 y T3. | Transición de estados | — |
| `test_cancel_en_datos_cliente_vuelve_al_carrito` | T5 conserva los productos. | Transición de estados | — |
| `test_datos_invalidos_no_avanzan` | T10: con error se queda en DATOS_CLIENTE. | Transición de estados | RF-02 |
| `test_checkout_con_carrito_vacio_se_impide` | TI-1. | Transición inválida | RF-07 · CP-14 |
| `test_orden_completada_no_se_puede_reconfirmar` | TI-2. | Transición inválida | RF-08 · CP-18 |
| `test_finish_con_carrito_cambiado_no_confirma` | TI-3: no confirma y recalcula el resumen. | Transición inválida | RF-08 · CP-19 |
| `test_add_to_cart_con_sesion_expirada` | TI-4. | Transición inválida | RF-10 · CP-20 |
| `test_agregar_id_inexistente_no_cambia_el_carrito` | TI-5. | Transición inválida | RF-01 |
| `test_producto_repetido_y_quitar_lo_que_no_esta` | No se duplica un producto ni se quita uno ausente. | Partición (inválida) | RF-01 |
| `test_acciones_fuera_de_orden_desde_vacio` (×4) | Ninguna acción del checkout funciona con el carrito vacío. | Transición inválida | RF-07 |

## Cobertura

```
Name                         Stmts   Miss Branch BrPart  Cover
src/checkout/carrito.py         77      0     16      0   100%
src/checkout/catalogo.py        20      0      8      0   100%
src/checkout/precios.py         26      0      4      0   100%
src/checkout/validacion.py      31      0     10      0   100%
TOTAL                          154      0     38      0   100%
```

Para comprobar que las pruebas detectan errores reales se metieron dos defectos a propósito:
cambiar `>=` por `>` en el umbral del descuento (falla la prueba de 100.00) y quitar el recorte
de espacios en la validación (fallan las pruebas de solo espacios y de recorte).
