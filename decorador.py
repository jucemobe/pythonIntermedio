# Decorador de validación sin imports externos (functools/inspect/numbers)

def validar(_func=None, *, tipo=None, minimo=None, maximo=None):
    """
    Decorador de validación de argumentos de entrada, sin dependencias externas.

    Parámetros opcionales:
        - tipo: un tipo o una tupla de tipos aceptados (p. ej., str o (int, float)).
        - minimo: valor mínimo permitido (solo se aplica a números reales).
        - maximo: valor máximo permitido (solo se aplica a números reales).

    Comportamiento:
        - Si 'tipo' está definido, valida cada argumento (posicional o con nombre).
        - Si 'minimo'/'maximo' están definidos, solo se aplican a int/float (excluye bool).
        - Los valores None no se validan (útil para parámetros opcionales).
        - Sin 'inspect', los nombres de parámetros posicionales no se conocen,
          por lo que los mensajes se referencian por índice (arg #0, #1, ...).
    """

    def _es_numero_real(x):
        # Consideramos int/float como números reales, excluyendo bool.
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def _tipos_str(t):
        if isinstance(t, tuple):
            return ", ".join(tt.__name__ for tt in t)
        return t.__name__

    def _decorador(func):
        def wrapper(*args, **kwargs):
            # Validar argumentos posicionales por índice
            if tipo is not None or minimo is not None or maximo is not None:
                for i, valor in enumerate(args):
                    if valor is None:
                        continue

                    # Validación de tipo
                    if tipo is not None and not isinstance(valor, tipo):
                        raise TypeError(
                            f"Argumento posicional #{i} debe ser de tipo {_tipos_str(tipo)}, "
                            f"recibió {type(valor).__name__}."
                        )

                    # Validación de rango (solo números reales)
                    if (minimo is not None or maximo is not None) and _es_numero_real(valor):
                        if minimo is not None and valor < minimo:
                            raise ValueError(
                                f"Argumento posicional #{i} = {valor} es menor que el mínimo ({minimo})."
                            )
                        if maximo is not None and valor > maximo:
                            raise ValueError(
                                f"Argumento posicional #{i} = {valor} excede el máximo ({maximo})."
                            )

                # Validar argumentos con nombre
                for k, valor in kwargs.items():
                    if valor is None:
                        continue

                    # Validación de tipo
                    if tipo is not None and not isinstance(valor, tipo):
                        raise TypeError(
                            f"Argumento '{k}' debe ser de tipo {_tipos_str(tipo)}, "
                            f"recibió {type(valor).__name__}."
                        )

                    # Validación de rango (solo números reales)
                    if (minimo is not None or maximo is not None) and _es_numero_real(valor):
                        if minimo is not None and valor < minimo:
                            raise ValueError(
                                f"Argumento '{k}' = {valor} es menor que el mínimo ({minimo})."
                            )
                        if maximo is not None and valor > maximo:
                            raise ValueError(
                                f"Argumento '{k}' = {valor} excede el máximo ({maximo})."
                            )

            return func(*args, **kwargs)

        # Replicar metadatos básicos sin functools.wraps
        wrapper.__name__ = getattr(func, "__name__", "wrapper")
        wrapper.__doc__ = getattr(func, "__doc__", None)
        wrapper.__module__ = getattr(func, "__module__", None)
        return wrapper

    # Permitir @validar y @validar(...)
    if callable(_func):
        return _decorador(_func)
    return _decorador


# =======================
# EJEMPLOS DE USO
# =======================

@validar(tipo=str)
def nombre_en_mayuscula(nombre):
    return nombre.title()

@validar(tipo=float, maximo=100, minimo=0)
def sumar(n1, n2):
    return n1 + n2


if __name__ == "__main__":
    # Pruebas rápidas (descomenta para probar):

    print(nombre_en_mayuscula("ana pérez"))  # -> "Ana Pérez"
    # nombre_en_mayuscula(123)               # TypeError

    print(sumar(10.5, 20.3))                 # -> 30.8
    # sumar(-1.0, 5.0)                       # ValueError (menor que mínimo 0)
    # sumar(50.0, 60.0)                      # ValueError (excede máximo 100)
    # sumar(10, 20)                          # TypeError (se exige float estricto)

    # Si quieres permitir int y float:
    # @validar(tipo=(int, float), maximo=100, minimo=0)
    # def sumar_flexible(n1, n2):
    #     return n1 + n2
    # print(sumar_flexible(10, 20))          # -> 30