from typing import List
from .models import CommandEvent
from .handlers import EventHandler


class EventBus:
    """
    Encargado de procesar eventos y distribuirlos a los handlers (gestores)
    """
    def __init__(self, *handlers: EventHandler):
        self._handlers = list(handlers)

    def append_handler(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    def process(self, *commands: str) -> None:
        for cmd in commands:
            ev = CommandEvent.now(cmd)
            for handler in self._handlers:
                handler.handle(ev)