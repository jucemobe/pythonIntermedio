import threading
import time

def monitor_mensaje():
    while True:
        print("Ejecutándose...\n")
        time.sleep(1)

hilo = threading.Thread(target=monitor_mensaje, name="monitor", daemon=True)
hilo.start()

# Mantén vivo el principal (o haz tu lógica aquí)
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Saliendo...")
