import threading
import queue
import time
import random


def generador_con_workers(cantidad_datos, num_workers=3):
    """
    Generador concurrente que produce tuplas (item, valor)
    donde:
      - item = "data_N"
      - valor = len(item)
    """

    cola_entrada = queue.Queue()
    cola_salida = queue.Queue()
    SENTINELA = object()

    def worker():
        while True:
            dato_id = cola_entrada.get()
            if dato_id is SENTINELA:
                cola_entrada.task_done()
                break

            # Simulación de procesamiento
            time.sleep(random.uniform(0.01, 0.05))

            item = f"data_{dato_id}"
            valor = len(item)

            cola_salida.put((item, valor))
            cola_entrada.task_done()

    # Crear workers
    for _ in range(num_workers):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    # Generar datos
    for i in range(1, cantidad_datos + 1):
        cola_entrada.put(i)

    # Señales de parada
    for _ in range(num_workers):
        cola_entrada.put(SENTINELA)

    # Generador de salida
    procesados = 0
    while procesados < cantidad_datos:
        resultado = cola_salida.get()
        procesados += 1
        yield resultado

    cola_entrada.join()