# diccionario.py
# Implementación de un "diccionario" SIN usar dict internamente.
# Estructura interna: dos listas paralelas: _keys y _values

class Diccionario:
    def __init__(self, tupla_claves=(), tupla_valores=()):
        if not isinstance(tupla_claves, tuple) or not isinstance(tupla_valores, tuple):
            raise TypeError("Diccionario(tupla_claves, tupla_valores) requiere dos tuplas.")
        if len(tupla_claves) != len(tupla_valores):
            raise ValueError("Las tuplas de claves y valores deben tener la misma longitud.")

        self._keys = []
        self._values = []

        # Insertamos respetando unicidad: si se repite clave, gana la última (estilo update)
        for k, v in zip(tupla_claves, tupla_valores):
            self[k] = v

    def _index_of(self, key):
        """Devuelve el índice de key en _keys o -1 si no existe."""
        # Búsqueda lineal (O(n)) porque no usamos dict.
        for i, k in enumerate(self._keys):
            if k == key:
                return i
        return -1

    # ---------- Comportamiento tipo dict ----------
    def __getitem__(self, key):
        idx = self._index_of(key)
        if idx == -1:
            raise KeyError(key)
        return self._values[idx]

    def __setitem__(self, key, value):
        idx = self._index_of(key)
        if idx == -1:
            self._keys.append(key)
            self._values.append(value)
        else:
            self._values[idx] = value

    def __delitem__(self, key):
        idx = self._index_of(key)
        if idx == -1:
            raise KeyError(key)
        self._keys.pop(idx)
        self._values.pop(idx)

    def __len__(self):
        return len(self._keys)

    def __contains__(self, key):
        return self._index_of(key) != -1

    def __repr__(self):
        # representación simple sin dict
        pares = ", ".join(f"{self._keys[i]!r}: {self._values[i]!r}" for i in range(len(self)))
        return f"Diccionario({{{pares}}})"

    # ---------- Métodos requeridos ----------
    def clear(self):
        """Deja el diccionario totalmente vacío."""
        self._keys = []
        self._values = []

    def copy(self):
        """Devuelve una copia del diccionario."""
        # Creamos con tuplas (cumpliendo la interfaz pedida)
        return Diccionario(tuple(self._keys), tuple(self._values))

    def items(self):
        """Devuelve lista de tuplas (clave, valor)."""
        return [(self._keys[i], self._values[i]) for i in range(len(self))]

    def keys(self):
        """Devuelve lista de claves."""
        return self._keys.copy()

    def values(self):
        """Devuelve lista de valores."""
        return self._values.copy()

    def pop(self, key):
        """Elimina una clave (y su valor) y devuelve el valor."""
        idx = self._index_of(key)
        if idx == -1:
            raise KeyError(key)
        self._keys.pop(idx)
        return self._values.pop(idx)

    def popitem(self):
        """
        Elimina un elemento y devuelve (clave, valor).
        En Python moderno, dict.popitem() es LIFO; aquí hacemos lo mismo:
        elimina el último insertado.
        """
        if len(self) == 0:
            raise KeyError("popitem(): diccionario vacío")
        k = self._keys.pop()
        v = self._values.pop()
        return (k, v)

    def update(self, other):
        """
        Añade claves que no tenga, y para claves existentes actualiza valores.
        'other' puede ser:
          - otro Diccionario
          - una lista/tupla iterable de pares (clave, valor)
        """
        if other is None:
            return

        if isinstance(other, Diccionario):
            # Iteramos sobre sus items (lista de tuplas)
            for k, v in other.items():
                self[k] = v
            return

        # Si es iterable de pares (k, v)
        for par in other:
            if (not isinstance(par, tuple)) or len(par) != 2:
                raise TypeError("update() espera un Diccionario o un iterable de tuplas (clave, valor).")
            k, v = par
            self[k] = v