from random import shuffle

PALO = "♠♥♣♦"
NUMEROS = ["A", "J", "Q", "K"] + [str(numero) for numero in range(2, 11)]
CARTAS = [(palo, numero) for palo in PALO for numero in NUMEROS] + [("🃟", "0"), ("🃏", "0")]

class Baraja:
    def __init__(self):
        self._baraja = CARTAS.copy()

    def barajar(self):
        shuffle(self._baraja)

    def repartir(self, n):
        if n > len(self._baraja):
            raise ValueError("No hay suficientes cartas para repartir")
        mano = self._baraja[:n]
        self._baraja = self._baraja[n:]
        return mano

    def cartas(self):
        return self._baraja.copy()

    def gestionar_carta(self, accion, carta=None, posicion=None, nueva_carta=None):
        """
        Gestiona cartas del mazo: añadir, eliminar o modificar.
        
        accion: "añadir", "eliminar", "modificar"
        carta: carta a eliminar o modificar (tupla)
        posicion: índice donde insertar/modificar (opcional)
        nueva_carta: carta nueva cuando se usa modificar
        """

        if accion == "añadir":
            if posicion is None:
                self._baraja.append(carta)
            else:
                self._baraja.insert(posicion, carta)
            return True

        elif accion == "eliminar":
            if carta in self._baraja:
                self._baraja.remove(carta)
                return True
            return False

        elif accion == "modificar":
            if carta not in self._baraja:
                return False

            idx = self._baraja.index(carta)
            if posicion is None:
                self._baraja[idx] = nueva_carta
            else:
                # eliminar la original y colocar la nueva donde se indique
                self._baraja.pop(idx)
                self._baraja.insert(posicion, nueva_carta)
            return True

        else:
            raise ValueError("Acción no válida. Usa: añadir, eliminar, modificar.")       