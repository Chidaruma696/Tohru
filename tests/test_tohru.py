import pytest

from tohru import (
    CAPACIDAD,
    PREFIJO_CAJA,
    PREFIJO_PESADA,
    Pesable,
    barcode_identidad,
    barcode_pesable,
    completar,
    decodificar,
    descomponer,
    digito_verificador,
    es_identidad,
    es_valido,
    estado_secuencia,
    preferir_viva,
    variantes,
)

# ---------------------------------------------------------------- ean13


def test_verificador_de_gtin_real():
    assert digito_verificador("750105922482") == "7"
    assert completar("750105922482") == "7501059224827"
    assert es_valido("7501059224827")
    assert not es_valido("7501059224820")


def test_es_valido_ignora_espacios_y_longitudes_raras():
    assert es_valido(" 7501 0592 24827 ")
    assert not es_valido("750105922482")
    assert not es_valido("")
    assert not es_valido(None)


def test_verificador_exige_doce_digitos():
    with pytest.raises(ValueError):
        digito_verificador("12345")
    with pytest.raises(ValueError):
        digito_verificador("12345678901A")


# ---------------------------------------------------------------- identidad


def test_identidad_compone_y_descompone():
    bc = barcode_identidad(PREFIJO_PESADA, 90050, 49006)
    assert len(bc) == 13 and bc.startswith("08") and es_valido(bc)
    assert descomponer(bc) == ("08", 90050, 49006)
    assert es_identidad(bc)


def test_identidad_plu_nulo_y_secuencia_modulo():
    assert barcode_identidad(PREFIJO_CAJA, None, 0)[:12] == "070000000000"
    assert barcode_identidad(PREFIJO_PESADA, 12, CAPACIDAD + 7)[7:12] == "00007"


def test_identidad_mismo_peso_distinta_secuencia_distinto_codigo():
    a = barcode_identidad(PREFIJO_PESADA, 635, 10)
    b = barcode_identidad(PREFIJO_PESADA, 635, 11)
    assert a != b


def test_identidad_tolera_cero_mutilado():
    bc = barcode_identidad(PREFIJO_PESADA, 3658, 42)
    assert descomponer(bc[1:]) == ("08", 3658, 42)
    assert es_identidad(bc[1:])


def test_identidad_rechaza_prefijo_y_rangos_malos():
    with pytest.raises(ValueError):
        barcode_identidad("8", 1, 1)
    with pytest.raises(ValueError):
        barcode_identidad("08", 100_000, 1)
    with pytest.raises(ValueError):
        barcode_identidad("08", 1, -1)


def test_descomponer_rechaza_lo_que_no_es_identidad():
    assert descomponer("7501059224827") is None  # GTIN comercial
    assert descomponer("2000023012507") is None  # pesable con prefijo 20
    assert descomponer("0890050490060") is None  # verificador malo
    assert descomponer("abc") is None


def test_estado_secuencia():
    e = estado_secuencia(49_005)
    assert e.usadas == 49_006
    assert e.restantes == 50_994
    assert not e.dio_la_vuelta
    assert e.meses_restantes(2_850) == pytest.approx(17.89, abs=0.01)
    assert e.meses_restantes(0) is None
    assert estado_secuencia(CAPACIDAD - 1).dio_la_vuelta
    assert estado_secuencia(CAPACIDAD + 5).restantes == 0


# ---------------------------------------------------------------- pesable


def test_pesable_ean13_y_upca():
    assert decodificar("2000023012507") == Pesable(plu=23, peso_kg=12.5, prefijo="20")
    assert decodificar("200023012501") == Pesable(plu=23, peso_kg=12.5, prefijo="2")  # 12 dígitos (UPC-A)


def test_pesable_en_gramos():
    assert decodificar("2000023012507", centesimas=False).peso_kg == pytest.approx(1.25)


def test_pesable_rechaza_identidad_plu_cero_y_basura():
    assert decodificar(barcode_identidad("08", 5, 5)) is None
    assert decodificar(barcode_identidad("08", 5, 5)[1:]) is None  # sin el 0 inicial
    assert decodificar("2000000012506") is None  # PLU 0
    assert decodificar("12345") is None
    assert decodificar(None) is None


def test_barcode_pesable_ida_y_vuelta():
    bc = barcode_pesable("20", 5080, 1.257)
    assert es_valido(bc)
    assert decodificar(bc) == Pesable(plu=5080, peso_kg=1.26, prefijo="20")
    with pytest.raises(ValueError):
        barcode_pesable("08", 1, 1.0)  # prefijo reservado
    with pytest.raises(ValueError):
        barcode_pesable("20", 1, 1000.0)  # no cabe en 5 dígitos


# ---------------------------------------------------------------- lector


def test_variantes_de_13_digitos_con_cero():
    assert variantes("0750105922482") == ["0750105922482", "075010592248", "750105922482"]


def test_variantes_de_12_y_11_digitos():
    assert variantes("750105922482") == ["750105922482", "7501059224827", "0750105922482"]
    v = variantes("75010592248")
    assert v[0] == "75010592248"
    assert "075010592248" in v
    assert any(len(x) == 13 and es_valido(x) for x in v)


def test_variantes_espacios_y_vacios():
    assert variantes("  ") == []
    assert variantes(None) == []
    assert variantes("7501 0592 24827")[:2] == ["7501 0592 24827", "7501059224827"]


def test_preferir_viva_gana_la_viva_aunque_no_sea_la_primera():
    muerta = {"barcode": "0000526000522", "estado": "anulado"}
    viva = {"barcode": "000526000522", "estado": "disponible"}
    assert preferir_viva([muerta, viva]) is viva
    assert preferir_viva([muerta]) is muerta
    assert preferir_viva([]) is None
    assert preferir_viva([{"estado": "cerrada"}], vivos=("abierta", "cerrada"))["estado"] == "cerrada"
