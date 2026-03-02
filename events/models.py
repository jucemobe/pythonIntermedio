from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CommandEvent:
    """Evento que representa un comando con timestamp."""
    name: str
    ts: datetime

    @staticmethod
    def now(name):
        """Crea un evento con timestamp actual en UTC."""
        return CommandEvent(name=name, ts=datetime.now(timezone.utc))