[🇪🇸 Español](README.md)

<div align="center">
  <br/>

# Tohru

**符 · Scale barcodes for Python, with no dependencies.**

<br/>

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/Chidaruma696/Tohru/ci.yml?branch=main&style=for-the-badge&label=pytest)](https://github.com/Chidaruma696/Tohru/actions)
![No dependencies](https://img.shields.io/badge/dependencies-0-1b150d?style=for-the-badge)
![MIT License](https://img.shields.io/badge/license-MIT-1b150d?style=for-the-badge)

<br/>

*EAN-13 · per-package identity · embedded weight · scanner tolerance*

</div>

---

> [!NOTE]
> Tohru is the Python half of a pair: **[Kana](https://github.com/Chidaruma696/Kana)** reads the scale from the browser and Tohru puts a code on whatever it weighed. Each one stands on its own; together they cover the full weigh, label and scan-back flow.

<br/>

## ⚖️ What it is

When you weigh a product and print a barcode label for it, there are two ways to encode it:

| 🔢 Classic variable-weight | 🪪 Identity |
| --- | --- |
| `[prefix][PLU][weight]` | `[prefix][PLU][sequence]` |
| The weight travels in the digits | The weight lives in your database |
| Two identical packages share a code | Every package gets its own, always |
| No database needed to ring it up | You can void, count and trace every single item |

Tohru implements both, plus everything needed around them: the EAN-13 check digit, and tolerance for handheld scanners that swallow the leading zero or the check digit. Everything is pure functions over strings; the code is never converted to an integer, because leading zeros carry meaning.

<br/>

## 📲 Install

```bash
pip install tohru
```

Until it's on PyPI, straight from the repository:

```bash
pip install git+https://github.com/Chidaruma696/Tohru.git
```

<br/>

## 🧪 Usage

### Per-package identity

```python
from tohru import barcode_identidad, descomponer, PREFIJO_PESADA

# Reserve the sequence BEFORE saving the row (a counter in your database) and
# save the row with its code already set: there is no intermediate state without a code.
secuencia = siguiente_secuencia()            # your database, your counter
codigo = barcode_identidad(PREFIJO_PESADA, plu=90050, secuencia=secuencia)
# '0890050490063'

descomponer("0890050490063")                 # ('08', 90050, 49006)
descomponer("890050490063")                  # the scanner swallowed the 0: same result
```

The sequence is five digits: a hundred thousand codes per prefix. Tohru tells you how much is left so it doesn't catch you by surprise:

```python
from tohru import estado_secuencia

e = estado_secuencia(ultima_secuencia=49_005)
e.restantes                 # 50994
e.meses_restantes(2_850)    # 17.9 months at that rate → switch prefixes before then
```

### Classic variable-weight

```python
from tohru import decodificar, barcode_pesable

decodificar("2000023012507")       # Pesable(plu=23, peso_kg=12.5, prefijo='20')
decodificar("0890050490063")       # None: it's an identity code, the weight is NOT in the digits
barcode_pesable("20", plu=5080, peso_kg=1.257)   # '2050800012' + check digit, rounded to hundredths
```

### Scanning with tolerance

```python
from tohru import variantes, preferir_viva

cands = variantes("750105922482")
# ['750105922482', '7501059224827', '0750105922482']
filas = db.execute("SELECT * FROM etiquetas WHERE barcode IN (...)", cands)
fila = preferir_viva(filas)        # if there are twins, the one still alive wins
```

`variantes` covers what a handheld scanner gets wrong: delivering 12 digits without the check digit, reading an EAN-13 as UPC-A without the zero, or both at once (11 digits). `preferir_viva` keeps a voided label with the same code from hijacking the scan of the one you're holding.

<br/>

## 🔧 API

| Module | Function | What it does |
| --- | --- | --- |
| `tohru.ean13` | `digito_verificador(base12)` | EAN-13 check digit for a twelve-digit base |
| | `completar(base12)` | Base plus check digit |
| | `es_valido(codigo)` | Thirteen digits with a correct check digit |
| | `solo_digitos(texto)` | Strips spaces and symbols |
| `tohru.identidad` | `barcode_identidad(prefijo, plu, secuencia)` | Identity code |
| | `descomponer(codigo)` | `(prefijo, plu, secuencia)` or `None` |
| | `es_identidad(codigo)` | Prefixes 07/08, with or without the leading zero |
| | `estado_secuencia(ultima)` | How much is left before wraparound |
| `tohru.pesable` | `decodificar(codigo, centesimas=True)` | `Pesable(plu, peso_kg, prefijo)` or `None` |
| | `barcode_pesable(prefijo, plu, peso_kg)` | Classic code with embedded weight |
| `tohru.lector` | `variantes(codigo)` | The forms a scanner may have delivered it in |
| | `preferir_viva(filas, vivos=...)` | The live row among twins |

The `08` (weighing) and `07` (box) prefixes are just the defaults. Any pair of digits that doesn't collide with your commercial GTINs will do; GS1 reserves `20` through `29` for in-store use.

<br/>

## 🔬 Development

```bash
git clone https://github.com/Chidaruma696/Tohru.git
cd Tohru
pip install -e .[dev]
pytest          # 22 tests plus the doctests
```

No runtime dependencies, typed (`py.typed`), Python 3.10 through 3.13 in CI.

<br/>

## ⚖️ License

[MIT](LICENSE).

<br/>

<div align="center">

*Every package with its own name.*

符 · ふ

</div>
