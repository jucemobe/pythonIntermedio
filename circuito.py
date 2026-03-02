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

from abc import ABC, abstractmethod

# --- Comandos ---
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

# --- Comandos ---
class Command:
    def execute(self) -> None:
        raise NotImplementedError("Subclases deben implementar 'execute'")

class ToggleCommand(Command):
    def __init__(self, device):  # duck typing: turn_on/turn_off/is_on
        self._device = device

    def execute(self) -> None:
        if self._device.is_on():
            self._device.turn_off()
        else:
            self._device.turn_on()

class TurnOnCommand(Command):
    def __init__(self, device):
        self._device = device

    def execute(self) -> None:
        self._device.turn_on()

class TurnOffCommand(Command):
    def __init__(self, device):
        self._device = device

    def execute(self) -> None:
        self._device.turn_off()

# --- Dispositivos ---
class Bombilla:
    def __init__(self, on=False):
        self._on = bool(on)

    def turn_on(self) -> None:
        self._on = True

    def turn_off(self) -> None:
        self._on = False

    def is_on(self) -> bool:
        return self._on

    def __repr__(self) -> str:
        return f"Bombilla(ON={self._on})"

class LedRGB:
    def __init__(self, on=False, color="blanco"):
        self._on = bool(on)
        self.color = color

    def turn_on(self) -> None:
        self._on = True

    def turn_off(self) -> None:
        self._on = False

    def is_on(self) -> bool:
        return self._on

    def set_color(self, color: str) -> None:
        self.color = color

    def __repr__(self) -> str:
        return f"LedRGB(ON={self._on}, color='{self.color}')"

# --- Circuito ---
class Circuito:
    def __init__(self):
        # listas simples; duck typing para dispositivos y callbacks
        self._dispositivos = []   # objetos con turn_on/turn_off/is_on
        self._listeners = []      # funciones que aceptan un str

    def agregar(self, dispositivo) -> None:
        # Verificación mínima por reflexión (fail-fast)
        required = ("turn_on", "turn_off", "is_on")
        if not all(hasattr(dispositivo, m) for m in required):
            raise TypeError("El dispositivo debe implementar turn_on/turn_off/is_on")
        self._dispositivos.append(dispositivo)
        self._notify(f"Dispositivo agregado: {dispositivo!r}")

    def dispositivos(self):
        return list(self._dispositivos)

    def on_event(self, callback) -> None:
        # callback debe aceptar un único str
        self._listeners.append(callback)

    def _notify(self, msg: str) -> None:
        for cb in self._listeners:
            cb(msg)

    def ejecutar(self, idx: int, cmd: Command) -> None:
        if not (0 <= idx < len(self._dispositivos)):
            raise IndexError("Índice de dispositivo inválido")
        cmd.execute()
        estado = "encendido" if self._dispositivos[idx].is_on() else "apagado"
        self._notify(f"Dispositivo[{idx}] ahora está {estado}")
