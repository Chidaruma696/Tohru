[🇬🇧 English](README.md)

<div align="center">
  <br/>

# Tohru

**符 · Códigos de barras de báscula para Python, sin dependencias.**

<br/>

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/Chidaruma696/Tohru/ci.yml?branch=main&style=for-the-badge&label=pytest)](https://github.com/Chidaruma696/Tohru/actions)
![Sin dependencias](https://img.shields.io/badge/dependencias-0-1b150d?style=for-the-badge)
![Licencia MIT](https://img.shields.io/badge/licencia-MIT-1b150d?style=for-the-badge)

<br/>

*EAN-13 · identidad por paquete · peso embebido · tolerancia a lectores*

</div>

---

> [!NOTE]
> Tohru es la mitad Python de un par: **[Kana](https://github.com/Chidaruma696/Kana)** lee la báscula desde el navegador y Tohru le pone código a lo que pesó. Cada una vive sola; juntas cubren el flujo completo de pesar, etiquetar y volver a leer.

<br/>

## ⚖️ Qué es

Cuando pesas un producto y le imprimes una etiqueta con código de barras, tienes dos formas de codificarlo:

| 🔢 Pesable clásico | 🪪 Identidad |
| --- | --- |
| `[prefijo][PLU][peso]` | `[prefijo][PLU][secuencia]` |
| El peso viaja en los dígitos | El peso vive en tu base de datos |
| Dos paquetes iguales comparten código | Cada paquete tiene el suyo, siempre |
| No necesitas base para cobrar | Puedes anular, contar y rastrear cada pieza |

Tohru implementa las dos, más lo que hace falta alrededor: el dígito verificador EAN-13, y la tolerancia a lectores de mano que se comen el cero inicial o el verificador. Todo son funciones puras sobre cadenas; nunca convierte el código a entero, porque los ceros a la izquierda significan.

<br/>

## 📲 Instalar

```bash
pip install tohru
```

Mientras no esté en PyPI, directo del repositorio:

```bash
pip install git+https://github.com/Chidaruma696/Tohru.git
```

<br/>

## 🧪 Uso

### Identidad por paquete

```python
from tohru import barcode_identidad, descomponer, PREFIJO_PESADA

# Reserva la secuencia ANTES de guardar la fila (un contador en tu base) y
# guarda la fila ya con su código: no hay estado intermedio sin código.
secuencia = siguiente_secuencia()            # tu base, tu contador
codigo = barcode_identidad(PREFIJO_PESADA, plu=90050, secuencia=secuencia)
# '0890050490063'

descomponer("0890050490063")                 # ('08', 90050, 49006)
descomponer("890050490063")                  # el lector se comió el 0: mismo resultado
```

La secuencia son cinco dígitos: cien mil códigos por prefijo. Tohru te dice cuánto queda para que no te sorprenda:

```python
from tohru import estado_secuencia

e = estado_secuencia(ultima_secuencia=49_005)
e.restantes                 # 50994
e.meses_restantes(2_850)    # 17.9 meses a ese ritmo → cambia de prefijo antes
```

### Pesable clásico

```python
from tohru import decodificar, barcode_pesable

decodificar("2000023012507")       # Pesable(plu=23, peso_kg=12.5, prefijo='20')
decodificar("0890050490063")       # None: es de identidad, el peso NO está en los dígitos
barcode_pesable("20", plu=5080, peso_kg=1.257)   # '2050800012' + verificador, redondeado a centésimas
```

### Escanear con tolerancia

```python
from tohru import variantes, preferir_viva

cands = variantes("750105922482")
# ['750105922482', '7501059224827', '0750105922482']
filas = db.execute("SELECT * FROM etiquetas WHERE barcode IN (...)", cands)
fila = preferir_viva(filas)        # si hay gemelas, gana la que sigue viva
```

`variantes` cubre lo que un lector de mano hace mal: entregar 12 dígitos sin verificador, leer un EAN-13 como UPC-A sin el cero, o las dos cosas a la vez (11 dígitos). `preferir_viva` evita que una etiqueta anulada con el mismo código secuestre el escaneo de la que tienes en la mano.

<br/>

## 🔧 API

| Módulo | Función | Qué hace |
| --- | --- | --- |
| `tohru.ean13` | `digito_verificador(base12)` | Verificador EAN-13 de doce dígitos |
| | `completar(base12)` | Base más verificador |
| | `es_valido(codigo)` | Trece dígitos con verificador correcto |
| | `solo_digitos(texto)` | Limpia espacios y símbolos |
| `tohru.identidad` | `barcode_identidad(prefijo, plu, secuencia)` | Código de identidad |
| | `descomponer(codigo)` | `(prefijo, plu, secuencia)` o `None` |
| | `es_identidad(codigo)` | Prefijos 07/08, con o sin cero inicial |
| | `estado_secuencia(ultima)` | Cuánto queda antes de la vuelta |
| `tohru.pesable` | `decodificar(codigo, centesimas=True)` | `Pesable(plu, peso_kg, prefijo)` o `None` |
| | `barcode_pesable(prefijo, plu, peso_kg)` | Código clásico con peso embebido |
| `tohru.lector` | `variantes(codigo)` | Formas en que un lector pudo entregarlo |
| | `preferir_viva(filas, vivos=...)` | La fila viva entre gemelas |

Los prefijos `08` (pesada) y `07` (caja) son solo el valor por defecto. Vale cualquier par de dígitos que no choque con tus GTIN comerciales; GS1 reserva `20` a `29` para uso interno de la tienda.

<br/>

## 🔬 Desarrollo

```bash
git clone https://github.com/Chidaruma696/Tohru.git
cd Tohru
pip install -e .[dev]
pytest          # 22 pruebas más los doctests
```

Sin dependencias en tiempo de ejecución, tipado (`py.typed`), Python 3.10 a 3.13 en CI.

<br/>

## ⚖️ Licencia

[MIT](LICENSE).

<br/>

<div align="center">

*Cada paquete con su nombre.*

符 · ふ

</div>
