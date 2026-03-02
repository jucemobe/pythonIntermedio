# # Codigo MAL diseñado! (no cumple quinto principio solid)

# class Bombilla:
#     def __init__(self):
#         self.on_off = False  # Apagada

# class Circuito:
#     def __init__(self):
#         self.bombilla = Bombilla()
        
#     def click(self):
#         self.bombilla.on_off = not self.bombilla.on_off
#         mensaje = "Bombilla encendida" if self.bombilla.on_off else "Bombilla apagada"
#         print(mensaje)

# c = Circuito()
# c.click()
# c.click()
# c.click()

from circuito import Circuito, Bombilla, LedRGB, ToggleCommand, TurnOnCommand, TurnOffCommand

logs = []
c = Circuito()
c.on_event(logs.append)

b1 = Bombilla()
b2 = Bombilla()
led = LedRGB(color="azul")

c.agregar(b1)
c.agregar(b2)
c.agregar(led)

c.ejecutar(0, ToggleCommand(b1))    # ON
c.ejecutar(1, TurnOnCommand(b2))    # ON
led.set_color("rojo")
c.ejecutar(2, ToggleCommand(led))   # ON
c.ejecutar(0, TurnOffCommand(b1))   # OFF

print("\n".join(logs))