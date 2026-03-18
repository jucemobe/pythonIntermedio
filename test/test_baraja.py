from codigo_pruebas import Baraja, CARTAS
from pytest import fixture

@fixture
def baraja():
    return Baraja()
    
def test_bajara(baraja):
    assert CARTAS == baraja._baraja
    baraja.barajar()
    assert CARTAS == baraja._baraja
    assert len(baraja._baraja) == 54
    
def test_baraja(baraja):
    primera_carta = baraja.primera_carta()
    assert primera_carta == ("♠", "A")
    ultima_carta = baraja.ultima_carta()
    assert ultima_carta == ("🃏", "0")
    baraja.colocar_carta(ultima_carta)
    assert baraja.primera_carta() == ultima_carta
    #assert len(baraja._baraja) == 54