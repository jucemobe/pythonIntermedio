from generadHilos import generador_con_workers


def test_total_elementos_procesados():
    gen = generador_con_workers(20, 4)
    resultados = list(gen)

    assert len(resultados) == 20


def test_procesamiento_correcto():
    gen = generador_con_workers(10, 3)

    for item, valor in gen:
        assert item.startswith("data_")
        assert valor == len(item)