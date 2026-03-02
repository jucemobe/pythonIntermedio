from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime
import json
import sys

from .models import CommandEvent


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: CommandEvent) -> None:
        ...


class JsonEventHandler(EventHandler):
    """
    - Crea JSON por evento
    - Mantiene contador por comando
    - Puede escribir a archivo (opcional)
    """
    def __init__(self, file_path: Optional[str] = None, pretty: bool = False):
        self.file_path = file_path
        self.pretty = pretty
        self._emitted = []       # lista de JSON strings
        self._counts = {}        # contador por comando

    def handle(self, event: CommandEvent) -> None:
        # contador
        self._counts[event.name] = self._counts.get(event.name, 0) + 1

        payload = {
            "type": "event",
            "name": event.name,
            "ts": event.ts.isoformat(),
            "count": self._counts[event.name],
        }

        text = json.dumps(payload, ensure_ascii=False, indent=2 if self.pretty else None)
        self._emitted.append(text)

        if self.file_path:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")

    @property
    def emitted(self):
        return list(self._emitted)

    @property
    def counts(self):
        return dict(self._counts)


class TxtEventHandler(EventHandler):
    """
    - Escribe una línea por evento
    - Timestamp en formato legible
    """
    def __init__(self, file_path: Optional[str] = None, time_format: str = "%Y-%m-%d %H:%M:%S%z"):
        self.file_path = file_path
        self.time_format = time_format
        self._lines = []

    def handle(self, event: CommandEvent) -> None:
        ts_local = event.ts.astimezone()
        line = f"[{ts_local.strftime(self.time_format)}] {event.name}"
        self._lines.append(line)

        if self.file_path:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    @property
    def lines(self):
        return list(self._lines)


class ConsoleEventHandler(EventHandler):
    """
    - Muestra eventos por pantalla (stdout o stderr)
    """
    def __init__(self, stream: str = "stdout"):
        self.stream = stream.lower()

    def handle(self, event: CommandEvent) -> None:
        msg = f"EVENT [{event.ts.isoformat()}] :: {event.name}"
        if self.stream == "stderr":
            print(msg, file=sys.stderr)
        else:
            print(msg)