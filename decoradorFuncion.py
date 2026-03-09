# ============================
# Decorador y utilidades
# ============================

from functools import wraps
from time import time

# Registro global: clave = función (objeto), valor = dict con datos
REGISTRO_EJECUCIONES = {}

def _identidad_funcion(func):
    """Crea una identidad legible para la función."""
    modulo = getattr(func, "__module__", "<mod>")
    nombre = getattr(func, "__qualname__", getattr(func, "__name__", "<func>"))
    return f"{modulo}.{nombre}"

def registrar(func):
    """
    Decorador que guarda:
      - cantidad de ejecuciones
      - último resultado devuelto
      - último instante de ejecución (epoch seconds)
    
    También lleva un registro global de todas las funciones decoradas.
    """
    identidad = _identidad_funcion(func)

    # Aseguramos entrada inicial en el registro
    REGISTRO_EJECUCIONES[func] = {
        "identidad": identidad,
        "funcion": func,
        "llamadas": 0,
        "ultimo_resultado": None,
        "ultimo_tiempo": None,
        # Si quieres, puedes guardar el último error también:
        "ultimo_error": None,
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        # No actualizamos el registro si la función lanza una excepción.
        try:
            resultado = func(*args, **kwargs)
        except Exception as e:
            REGISTRO_EJECUCIONES[func]["ultimo_error"] = e
            # Repropagar el error para no alterar el comportamiento de la función
            raise
        else:
            info = REGISTRO_EJECUCIONES[func]
            info["llamadas"] += 1
            info["ultimo_resultado"] = resultado
            info["ultimo_tiempo"] = time()
            info["ultimo_error"] = None
            return resultado

    return wrapper


# ============================
# API de consulta del registro
# ============================

def listar_funciones_registradas():
    """
    Devuelve una lista de identidades de las funciones que usan @registrar.
    """
    return [info["identidad"] for info in REGISTRO_EJECUCIONES.values()]

def obtener_info(func):
    """
    Devuelve el diccionario de info para una función decorada concreta.
    Clavea por el objeto función, no por el nombre.
    """
    if func not in REGISTRO_EJECUCIONES:
        raise KeyError("La función no está registrada con @registrar.")
    return REGISTRO_EJECUCIONES[func].copy()

def ultimo_resultado(func):
    """
    Devuelve el último resultado registrado para 'func'.
    """
    return obtener_info(func)["ultimo_resultado"]

def resumen_registro():
    """
    Devuelve una lista de resúmenes legibles: (identidad, llamadas, ultimo_resultado).
    Útil para imprimir todos de una vez.
    """
    res = []
    for info in REGISTRO_EJECUCIONES.values():
        res.append({
            "identidad": info["identidad"],
            "llamadas": info["llamadas"],
            "ultimo_resultado": info["ultimo_resultado"],
            "ultimo_error": info["ultimo_error"],
            "ultimo_tiempo": info["ultimo_tiempo"],
        })
    return res


# ============================
# Ejemplos de uso
# ============================
if __name__ == "__main__":
    @registrar
    def sumar(a, b):
        return a + b

    @registrar
    def nombre_en_mayuscula(nombre):
        return str(nombre).title()

    # Ejecutamos algunas llamadas
    print("sumar(10, 20) ->", sumar(10, 20))           # 30
    print("sumar(5, 3)  ->", sumar(5, 3))              # 8
    print("nombre_en_mayuscula('ana pérez') ->", nombre_en_mayuscula("ana pérez"))

    # Consultas:
    print("\nFunciones registradas:")
    for ident in listar_funciones_registradas():
        print(" -", ident)

    print("\nÚltimo resultado de 'sumar':", ultimo_resultado(sumar))  # debería ser 8
    print("Último resultado de 'nombre_en_mayuscula':", ultimo_resultado(nombre_en_mayuscula))

    print("\nResumen de registro:")
    for r in resumen_registro():
        print(f"{r['identidad']} | llamadas={r['llamadas']} | "
              f"ultimo_resultado={r['ultimo_resultado']} | "
              f"ultimo_error={r['ultimo_error']} | "
              f"ultimo_tiempo={r['ultimo_tiempo']}")