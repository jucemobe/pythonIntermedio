import threading
import time
from datetime import datetime

# --- Función que imprime el nombre del hilo y espera 1 segundo ---
def tarea():
    nombre = threading.current_thread().name
    print(f"Iniciando {nombre} a las {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    time.sleep(1)
    print(f"Finalizando {nombre} a las {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

# Medimos el tiempo total
inicio = time.perf_counter()

# Creamos 4 hilos y los lanzamos concurrentemente
hilos = [threading.Thread(target=tarea, name=f"hilo-{i+1}") for i in range(4)]
for h in hilos:
    h.start()
for h in hilos:
    h.join()

fin = time.perf_counter()
tiempo_total = fin - inicio
print(f"Tiempo total: {tiempo_total:.3f} segundos")