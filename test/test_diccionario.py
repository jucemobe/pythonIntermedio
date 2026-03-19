# test_diccionario.py
import pytest
from diccionario import Diccionario

# 1 fixture (como pides)
@pytest.fixture
def dic():
    return Diccionario(("a", "b", "c"), (1, 2, 3))


# 1) Crearse como Diccionario(tupla_claves, tupla_valores)
def test_creacion(dic):
    assert len(dic) == 3
    assert dic["a"] == 1
    assert dic["b"] == 2
    assert dic["c"] == 3


# 2) Mostrar un valor como <nombre>[clave]
def test_getitem(dic):
    assert dic["b"] == 2
    with pytest.raises(KeyError):
        _ = dic["z"]


# 3) Cambiar un valor como <nombre>[clave] = valor
def test_setitem_cambia_existente(dic):
    dic["b"] = 99
    assert dic["b"] == 99
    assert len(dic) == 3


# 4) Cambiar / añadir clave nueva con <nombre>[clave] = valor
def test_setitem_añade_nueva(dic):
    dic["z"] = 7
    assert dic["z"] == 7
    assert len(dic) == 4


# 5) Eliminar un valor como del <nombre>[clave]
def test_delitem(dic):
    del dic["b"]
    assert len(dic) == 2
    with pytest.raises(KeyError):
        _ = dic["b"]
    with pytest.raises(KeyError):
        del dic["b"]


# 6) clear() deja el diccionario totalmente vacío
def test_clear(dic):
    dic.clear()
    assert len(dic) == 0
    assert dic.items() == []


# 7) copy() devuelve una copia del diccionario
def test_copy(dic):
    c = dic.copy()
    assert c.items() == dic.items()
    assert c is not dic
    # comprobar que es independiente
    c["a"] = 999
    assert dic["a"] == 1
    assert c["a"] == 999


# 8) items() -> lista de tuplas (clave, valor)
def test_items(dic):
    assert dic.items() == [("a", 1), ("b", 2), ("c", 3)]


# 9) keys() -> lista con sus claves
def test_keys(dic):
    assert dic.keys() == ["a", "b", "c"]


# 10) values() -> lista con sus valores
def test_values(dic):
    assert dic.values() == [1, 2, 3]


# 11) pop() elimina una clave (y su valor) y devuelve el valor
def test_pop(dic):
    v = dic.pop("b")
    assert v == 2
    assert len(dic) == 2
    with pytest.raises(KeyError):
        _ = dic["b"]
    with pytest.raises(KeyError):
        dic.pop("b")


# 12) popitem() elimina un valor (y su clave) y devuelve (clave, valor)
def test_popitem(dic):
    k, v = dic.popitem()
    assert (k, v) == ("c", 3)   # LIFO: último insertado
    assert len(dic) == 2
    with pytest.raises(KeyError):
        # vaciamos y probamos error
        d2 = Diccionario((), ())
        d2.popitem()


# BONUS (si quieres sustituir alguno): update()
def test_update(dic):
    dic.update([("b", 20), ("d", 4)])
    assert dic["b"] == 20
    assert dic["d"] == 4
    assert len(dic) == 4