import threading
import time
import random


def en_paralelo(n):
    def decorador(func):
        def wrapper(*args, **kwargs):
            resultados = []
            lock = threading.Lock()
            hilos = []

            def ejecutar():
                resultado = func(*args, **kwargs)
                with lock:
                    resultados.append(resultado)

            # Lanzar la función n veces en hilos distintos
            for _ in range(n):
                t = threading.Thread(target=ejecutar)
                t.start()
                hilos.append(t)

            # Esperar a que terminen todos
            for t in hilos:
                t.join()

            # Print ANTES del return (como pediste)
            print(resultados)

            return resultados

        return wrapper
    return decorador


# ============================
# EJEMPLO DE USO
# ============================

@en_paralelo(5)
def trabajo():
    time.sleep(random.uniform(0.1, 0.4))
    return threading.current_thread().name


if __name__ == "__main__":
    trabajo()