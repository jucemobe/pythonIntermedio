import threading
import time
from datetime import datetime

def mostrar_hora():
    while True:
        ahora = datetime.now().strftime("%H:%M:%S")
        print(f"La hora actual es: {ahora}")
        time.sleep(10)  # Espera 10 segundos

# Crear el hilo
hilo_hora = threading.Thread(target=mostrar_hora, daemon=True)

# Iniciar el hilo
hilo_hora.start()

# Mantener el programa principal vivo
print("Mostrando la hora cada 10 segundos. Pulsa Ctrl+C para salir.")
while True:
    time.sleep(1)