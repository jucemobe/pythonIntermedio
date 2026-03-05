# -*- coding: utf-8 -*-

# ============================
#  Generador e Iterador de letras intermedias
#  - Generador: letras_intermedias_gen
#  - Iterador:  LetrasIntermedias
#  - Alfabeto por defecto: español (incluye 'ñ')
# ============================

ALFABETO_ES = "abcdefghijklmnñopqrstuvwxyz"
ALFABETO_ES_MIXTO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ" + ALFABETO_ES

def letras_intermedias_gen(a, b, alfabeto=ALFABETO_ES):
    """
    Genera (yields) las letras estrictamente intermedias entre 'a' y 'b',
    excluyendo ambos extremos.

    Parámetros:
      - a (str): carácter inicial (longitud 1)
      - b (str): carácter final (longitud 1)
      - alfabeto (str|None): cadena que define el orden; si es None usa códigos Unicode.

    Notas:
      - Si 'alfabeto' es una cadena (por defecto, alfabeto español), se usa su índice.
      - Si 'alfabeto' es None, se usa el valor Unicode (ord/chr), útil para ASCII.
      - Soporta orden ascendente y descendente (a < b o a > b).
      - Si a == b o son adyacentes en el alfabeto, no produce nada.
      - Sensible a mayúsculas si el alfabeto las incluye. Puedes usar ALFABETO_ES_MIXTO.
    """
    if not isinstance(a, str) or not isinstance(b, str) or len(a) != 1 or len(b) != 1:
        raise ValueError("Debes pasar dos caracteres de longitud 1 para 'a' y 'b'.")

    if alfabeto is None:
        # Modo por código Unicode (ASCII típico)
        start, end = ord(a), ord(b)
        if start == end:
            return
        step = 1 if start < end else -1
        for code in range(start + step, end, step):
            yield chr(code)
    else:
        # Modo por alfabeto personalizado
        if len(set(alfabeto)) != len(alfabeto):
            raise ValueError("El alfabeto no debe tener caracteres repetidos.")
        try:
            ia, ib = alfabeto.index(a), alfabeto.index(b)
        except ValueError:
            raise ValueError("Ambas letras deben existir dentro del alfabeto proporcionado.")

        if ia == ib:
            return
        step = 1 if ia < ib else -1
        for i in range(ia + step, ib, step):
            yield alfabeto[i]


class LetrasIntermedias:
    """
    Iterador que recorre las letras intermedias entre 'a' y 'b'
    (excluye extremos). Soporta alfabeto personalizado.

    Ejemplo:
        list(LetrasIntermedias('l', 'p', ALFABETO_ES))  # ['m', 'n', 'ñ', 'o']
    """
    def __init__(self, a, b, alfabeto=ALFABETO_ES):
        if not isinstance(a, str) or not isinstance(b, str) or len(a) != 1 or len(b) != 1:
            raise ValueError("Debes pasar dos caracteres de longitud 1 para 'a' y 'b'.")

        self.alfabeto = alfabeto
        if alfabeto is None:
            # Modo Unicode
            self._mode = "unicode"
            self.start = ord(a)
            self.end = ord(b)
            if self.start == self.end:
                self.step = 1  # el valor no importa porque se detendrá en la primera comprobación
            else:
                self.step = 1 if self.start < self.end else -1
            self._cursor = self.start + self.step
        else:
            # Modo alfabeto personalizado
            self._mode = "custom"
            if len(set(alfabeto)) != len(alfabeto):
                raise ValueError("El alfabeto no debe tener caracteres repetidos.")
            try:
                ia, ib = alfabeto.index(a), alfabeto.index(b)
            except ValueError:
                raise ValueError("Ambas letras deben existir dentro del alfabeto proporcionado.")
            self.start = ia
            self.end = ib
            if ia == ib:
                self.step = 1  # igual que arriba: no se iterará nada
            else:
                self.step = 1 if ia < ib else -1
            self._cursor = self.start + self.step

    def __iter__(self):
        return self

    def __next__(self):
        if self._mode == "unicode":
            if (self.step == 1 and self._cursor >= self.end) or (self.step == -1 and self._cursor <= self.end):
                raise StopIteration
            ch = chr(self._cursor)
            self._cursor += self.step
            return ch
        else:
            if (self.step == 1 and self._cursor >= self.end) or (self.step == -1 and self._cursor <= self.end):
                raise StopIteration
            ch = self.alfabeto[self._cursor]
            self._cursor += self.step
            return ch


# ============================
# Ejemplos de uso / Pruebas rápidas
# ============================
if __name__ == "__main__":
    print("=== Generador con alfabeto español por defecto ===")
    print(list(letras_intermedias_gen('a', 'f')))        # ['b', 'c', 'd', 'e']
    print(list(letras_intermedias_gen('f', 'a')))        # ['e', 'd', 'c', 'b']
    print(list(letras_intermedias_gen('a', 'b')))        # []

    print("\n=== Generador con alfabeto mixto (mayúsculas y minúsculas) ===")
    print(list(letras_intermedias_gen('A', 'D', ALFABETO_ES_MIXTO)))  # ['B', 'C']
    print(list(letras_intermedias_gen('l', 'p', ALFABETO_ES)))        # ['m', 'n', 'ñ', 'o']

    print("\n=== Generador en modo Unicode (no contempla 'ñ' contigua a 'n') ===")
    print(list(letras_intermedias_gen('a', 'f', alfabeto=None)))      # ['b', 'c', 'd', 'e']

    print("\n=== Iterador con alfabeto español por defecto ===")
    print(list(LetrasIntermedias('a', 'f')))             # ['b', 'c', 'd', 'e']
    print(list(LetrasIntermedias('p', 'l')))             # ['o', 'ñ', 'n', 'm']
    print(list(LetrasIntermedias('l', 'p', ALFABETO_ES)))# ['m', 'n', 'ñ', 'o']

    print("\n=== Iterador con alfabeto mixto (mayúsculas y minúsculas) ===")
    print(list(LetrasIntermedias('A', 'F', ALFABETO_ES_MIXTO)))  # ['B', 'C', 'D', 'E']