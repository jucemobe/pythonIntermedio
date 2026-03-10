from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Iterable, Mapping
import json
import csv
import os


# =========================
# Estrategia (interfaz)
# =========================
class IWriter(ABC):
    @abstractmethod
    def write(self, path: Path, data: Dict[str, Any]) -> None:
        """
        Escribe 'data' en el archivo 'path'.
        Debe asumir que 'path' existe (puede estar vacío o no según política del sistema).
        """
        ...


# =========================
# Estrategias concretas
# =========================
class JsonWriter(IWriter):
    def __init__(self, *, indent: int = 2, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def write(self, path: Path, data: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=self.indent, ensure_ascii=self.ensure_ascii)


class CsvWriter(IWriter):
    """
    Escribe un diccionario como CSV de una sola fila.
    - Las claves del dict serán las cabeceras.
    - Los valores que no sean escalares se serializan como JSON.
    """
    def __init__(self, *, delimiter: str = ","):
        self.delimiter = delimiter

    @staticmethod
    def _normalize_value(value: Any) -> str:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return "" if value is None else str(value)
        # dict, list, etc. → lo metemos como JSON
        return json.dumps(value, ensure_ascii=False)

    def write(self, path: Path, data: Dict[str, Any]) -> None:
        if not isinstance(data, Mapping):
            raise TypeError("Para CSV, 'data' debe ser un diccionario (mapping).")

        headers = list(data.keys())
        row = [self._normalize_value(data[k]) for k in headers]

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            writer.writerow(headers)
            writer.writerow(row)


class TxtWriter(IWriter):
    """
    Escribe clave: valor por línea. Los valores no escalares se serializan como JSON.
    """
    def write(self, path: Path, data: Dict[str, Any]) -> None:
        lines: Iterable[str] = []
        for k, v in data.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                val = "" if v is None else str(v)
            else:
                val = json.dumps(v, ensure_ascii=False)
            lines.append(f"{k}: {val}")

        with path.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# =========================
# Sistema seleccionador (Contexto)
# =========================
@dataclass
class FileWriterSystem:
    """
    Selecciona la estrategia por extensión:
      - .json → JsonWriter
      - .csv  → CsvWriter
      - .txt  → TxtWriter
    """
    strategies: Dict[str, IWriter]

    @classmethod
    def default(cls) -> "FileWriterSystem":
        return cls(
            strategies={
                ".json": JsonWriter(),
                ".csv": CsvWriter(),
                ".txt": TxtWriter(),
            }
        )

    def _ensure_target(
        self,
        path: Path,
        *,
        create_if_missing: bool,
        allow_non_empty: bool,
    ) -> None:
        """
        Garantiza que el archivo existe y cumple las políticas de tamaño/permisos.
        Si no existe y create_if_missing=True, lo crea vacío.
        """
        if not path.exists():
            if create_if_missing:
                # Crea el directorio si no existe
                if not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                # Crea el archivo vacío
                path.touch(exist_ok=True)
            else:
                raise FileNotFoundError(
                    f"El archivo no existe: {path} (usa create_if_missing=True para crearlo)"
                )

        if not path.is_file():
            raise ValueError(f"No es un archivo: {path}")

        try:
            size = path.stat().st_size
        except OSError as e:
            raise OSError(f"No se pudo acceder a estadísticos del archivo: {path}") from e

        if not allow_non_empty and size != 0:
            raise ValueError(f"El archivo no está vacío (tamaño={size} bytes): {path}")

        if not os.access(path, os.W_OK):
            raise PermissionError(f"No hay permisos de escritura sobre: {path}")

    def _pick_strategy(self, path: Path, forced_kind: Optional[str] = None) -> IWriter:
        """
        forced_kind: opcional ('json' | 'csv' | 'txt'), para forzar estrategia.
        Si no se fuerza, se usa la extensión del archivo.
        """
        if forced_kind:
            key = f".{forced_kind.lower()}"
        else:
            key = path.suffix.lower()

        strategy = self.strategies.get(key)
        if strategy is None:
            raise ValueError(
                f"No hay estrategia para '{key}'. "
                f"Extensiones soportadas: {', '.join(self.strategies.keys())}"
            )
        return strategy

    def write(
        self,
        target: str | Path,
        data: Dict[str, Any],
        *,
        kind: Optional[str] = None,
        create_if_missing: bool = False,
        allow_non_empty: bool = False,
    ) -> None:
        """
        Escribe 'data' en 'target'.
        - 'kind' permite forzar 'json' | 'csv' | 'txt' (si la extensión no es fiable).
        - 'create_if_missing': crea el archivo si no existe (por defecto False).
        - 'allow_non_empty': permite escribir aunque el archivo tenga datos (por defecto False).
          * Si True, se SOBRESCRIBE el archivo (modo 'w').
        """
        path = Path(target)

        # Validación/creación según flags
        self._ensure_target(path, create_if_missing=create_if_missing, allow_non_empty=allow_non_empty)

        if not isinstance(data, Mapping):
            raise TypeError("'data' debe ser un diccionario (mapping).")

        strategy = self._pick_strategy(path, forced_kind=kind)
        strategy.write(path, data)


# =========================
# Ejemplos de uso
# =========================
if __name__ == "__main__":
    system = FileWriterSystem.default()

    datos: Dict[str, Any] = {
        "user": "joaquin",
        "likes": 121,
        "activo": True,
        "perfil": {"rol": "admin", "tags": ["a", "b"]},
        "notas": None,
    }

    # Cambia estas rutas por las tuyas. Aunque no existan, con create_if_missing=True se crearán.
    path_json = Path("./salida/ejemplo.json")
    path_csv = Path("./salida/ejemplo.csv")
    path_txt = Path("./salida/ejemplo.txt")

    # Crear si no existe y exigir que esté vacío
    system.write(path_json, datos, create_if_missing=True)        # JSON
    system.write(path_csv, datos, create_if_missing=True)         # CSV
    system.write(path_txt, datos, create_if_missing=True)         # TXT

    # Si quieres sobreescribir un archivo que ya tiene datos:
    # system.write(path_csv, datos, create_if_missing=True, allow_non_empty=True)

    print("Hecho. Revisa los archivos en ./salida/")
