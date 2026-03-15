suma = 0

while True:
    entrada = input("Introduce un número (o una letra para salir): ")

    # Intentamos convertir a número
    if entrada.isdigit() or (entrada.startswith('-') and entrada[1:].isdigit()):
        suma += int(entrada)
        print(f"Suma actual: {suma}")
    else:
        print("Entrada no numérica detectada. Terminando...")
        break

print(f"La suma final es: {suma}")