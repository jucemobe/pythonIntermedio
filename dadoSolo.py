import random

# ============================================================
# 1) GENERADOR DE DADO (infinito)
# ============================================================

def dado(caras=6):
    """
    Generador infinito de tiradas de un dado de 'caras' caras.
    Cada iteración produce un entero en [1, caras].
    """
    if not isinstance(caras, int) or caras < 2:
        raise ValueError("El número de caras debe ser un entero >= 2.")
    while True:
        yield random.randint(1, caras)


# ============================================================
# 2) CLASE Dado (iterable infinito, con soporte de caras y pesos)
# ============================================================

class Dado:
    """
    Dado iterable: al iterarlo produce tiradas aleatorias infinitas.
    Por defecto 6 caras, valores enteros de 1..caras.
    También puede recibir una lista de caras personalizadas.
    Permite pesos opcionales para probabilidades desiguales.
    """

    def __init__(self, caras=6, pesos=None):
        if isinstance(caras, int):
            if caras < 2:
                raise ValueError("El número de caras debe ser >= 2.")
            self._caras = list(range(1, caras + 1))
        else:
            self._caras = list(caras)
            if len(self._caras) < 2:
                raise ValueError("Debe haber al menos 2 caras.")

        if pesos is not None:
            pesos = list(pesos)
            if len(pesos) != len(self._caras):
                raise ValueError("Pesos debe tener la misma longitud que caras.")
            if any(p < 0 for p in pesos):
                raise ValueError("Los pesos no pueden ser negativos.")
            self._pesos = pesos
        else:
            self._pesos = None

    def __iter__(self):
        while True:
            if self._pesos is None:
                yield random.choice(self._caras)
            else:
                yield random.choices(self._caras, weights=self._pesos, k=1)[0]

    def tirar(self):
        """Lanza el dado una vez sin necesidad de iterarlo."""
        return next(iter(self))


# ============================================================
# 3) CLASE DadoIterador (la propia instancia es el iterador)
# ============================================================

class DadoIterador:
    """
    La instancia es su propio iterador, produce tiradas infinitas.
    """

    def __init__(self, caras=6):
        if not isinstance(caras, int) or caras < 2:
            raise ValueError("El número de caras debe ser >= 2.")
        self._caras = caras

    def __iter__(self):
        return self

    def __next__(self):
        return random.randint(1, self._caras)


# ============================================================
# EJEMPLOS DE USO
# ============================================================

if __name__ == "__main__":

    print("=== Generador ===")
    g = dado(6)
    for _ in range(5):
        print(next(g))

    print("\n=== Clase Dado estándar ===")
    d1 = Dado(6)
    for _, valor in zip(range(5), d1):
        print(valor)

    print("\n=== Clase Dado con caras personalizadas ===")
    d2 = Dado(["A", "B", "C"])
    for _, valor in zip(range(5), d2):
        print(valor)

    print("\n=== Clase Dado ponderado ===")
    d3 = Dado(6, pesos=[1, 1, 1, 1, 1, 3])  # el 6 sale más veces
    for _, valor in zip(range(10), d3):
        print(valor)

    print("\n=== Clase DadoIterador ===")
    d4 = DadoIterador(6)
    for _, valor in zip(range(5), d4):
        print(valor)