class Diccionario:
    def __init__(self, claves:tuple, valores:tuple):
        self.claves = list(claves)
        self.valores = list(valores)
        if len(self.claves) > len(self.valores):
            self.valores += [None] * (len(self.claves) - len(self.valores))
        elif len(self.valores) > len(self.claves):
            self.valores = self.valores[:len(self.claves)]
    def __getitem__(self, clave):
        indice_clave = self.claves.index(clave)
        return self.valores[indice_clave]
    def __setitem__(self, clave, valor):
        indice_clave = self.claves.index(clave)
        self.valores[indice_clave] = valor
    def __delitem__(self, clave):
        indice_clave = self.claves.index(clave)
        self.claves.pop(indice_clave)
        self.valores.pop(indice_clave)
    def clear(self):
        self.claves = []
        self.valores = []
    def copy(self):
        return Diccionario(self.claves.copy(), self.valores.copy())
    def items(self):
        return list(zip(self.claves, self.valores)) 
    def keys(self):
        return self.claves
    def values(self):
        return self.valores
    def pop(self, clave):
        indice_clave = self.claves.index(clave)
        valor = self.valores[indice_clave]
        del self[clave]
        return valor
    def popitem(self,valor):
        indice_valor = self.valores.index(valor)
        clave = self.claves[indice_valor]
        del self[clave]
        return clave, valor
    def update(self, otros_claves:tuple, otros_valores:tuple):
        for otra_clave in otros_claves:
            if otra_clave in self.claves:
                indice_clave = self.claves.index(otra_clave)
                indice_otra_clave = otros_claves.index(otra_clave)
                self.valores[indice_clave] = otros_valores[indice_otra_clave]
            else:
                self.claves.append(otra_clave)
                indice_otra_clave = otros_claves.index(otra_clave)
                self.valores.append(otros_valores[indice_otra_clave])
    def __contains__(self, clave: str) -> any:
        return clave in self.keys()
    def __add__(self, other):
        nuevo_dicc = Diccionario(self.claves, self.valores)
        nuevo_dicc.update(other.claves, other.valores)
        return nuevo_dicc
    def __or__(self, other):
        self.update(other.claves, other.valores)
    def __gt__(self, other):
        return len(self.items()) > len(other.items())
    def __ge__(self, other):
        return len(self.items()) >= len(other.items())
    def __lt__(self, other):
        return len(self.items()) < len(other.items())
    def __le__(self, other):
        return len(self.items()) <= len(other.items())
    def __eq__(self, other):
        for tupla_clave_valor in self.items():
            if tupla_clave_valor in other.items():
                continue
            else:
                return False
        if len(self.items()) != len(other.items()):
            return False
        return True
    def __ne__(self, other):
        if self == other:
            return False
        return True