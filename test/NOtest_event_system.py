# tests/test_event_system.py
# Tests para el sistema de eventos (bus + handlers JSON/TXT/Console)
# Requiere la estructura modular propuesta:
#  - events/models.py
#  - events/handlers.py
#  - events/bus.py

import json
import re
from pathlib import Path

import pytest

from events.bus import EventBus
from events.handlers import JsonEventHandler, TxtEventHandler, ConsoleEventHandler


def test_json_handler_counts_and_emitted(tmp_path: Path):
    out_file = tmp_path / "events.jsonl"
    h = JsonEventHandler(file_path=str(out_file), pretty=False)
    bus = EventBus(h)

    commands = ["login", "logout", "error", "login"]
    bus.process(*commands)

    # Contadores por comando
    assert h.counts == {"login": 2, "logout": 1, "error": 1}

    # Se ha emitido un JSON por evento
    assert len(h.emitted) == len(commands)

    # Cada línea es JSON válido con las claves esperadas
    for item in h.emitted:
        data = json.loads(item)
        assert set(data.keys()) == {"type", "name", "ts", "count"}
        assert data["type"] == "event"
        assert data["name"] in commands
        # Timestamp en ISO-8601 (formato básico: contiene una 'T')
        assert "T" in data["ts"]

    # Archivo creado: 4 líneas
    content_lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(content_lines) == len(commands)
    # Cada línea del archivo también es JSON válido
    for line in content_lines:
        json.loads(line)


def test_txt_handler_lines_and_order(tmp_path: Path):
    out_file = tmp_path / "events.log"
    h = TxtEventHandler(file_path=str(out_file))
    bus = EventBus(h)

    commands = ["login", "open", "user auth", "logout", "close"]
    bus.process(*commands)

    # Debe tener tantas líneas como eventos
    assert len(h.lines) == len(commands)

    # Orden preservado y formato básico esperado
    for i, cmd in enumerate(commands):
        line = h.lines[i]
        assert line.startswith("[") and "] " in line
        assert line.endswith(cmd)

    # Archivo contiene exactamente lo mismo
    file_lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert file_lines == h.lines


def test_console_handler_stdout_and_stderr(capsys):
    # stdout
    h_out = ConsoleEventHandler(stream="stdout")
    bus_out = EventBus(h_out)
    bus_out.process("login", "logout")

    out, err = capsys.readouterr()
    assert err == ""
    out_lines = [x for x in out.strip().splitlines() if x.strip()]
    assert len(out_lines) == 2
    assert "login" in out_lines[0]
    assert "logout" in out_lines[1]

    # stderr
    h_err = ConsoleEventHandler(stream="stderr")
    bus_err = EventBus(h_err)
    bus_err.process("error")

    out2, err2 = capsys.readouterr()
    assert out2 == ""
    assert "error" in err2


def test_bus_multiple_handlers_and_append(tmp_path: Path):
    # Arrancamos con sólo JSON, luego añadimos TXT y verificamos que ambos reciben eventos
    json_file = tmp_path / "events.jsonl"
    txt_file = tmp_path / "events.log"

    h_json = JsonEventHandler(file_path=str(json_file))
    bus = EventBus(h_json)

    # Primer batch: sólo JSON
    bus.process("a", "b")
    assert len(h_json.emitted) == 2

    # Añadimos TXT y procesamos más
    h_txt = TxtEventHandler(file_path=str(txt_file))
    bus.append_handler(h_txt)

    bus.process("c", "d", "e")

    # JSON recibió 5 en total
    assert len(h_json.emitted) == 5
    # TXT recibió 3 (los del segundo batch)
    assert len(h_txt.lines) == 3

    # Archivos existen y tienen el número de líneas esperado
    assert json_file.exists()
    assert txt_file.exists()
    assert len(json_file.read_text(encoding="utf-8").strip().splitlines()) == 5
    assert len(txt_file.read_text(encoding="utf-8").strip().splitlines()) == 3


def test_json_pretty_formatting(tmp_path: Path):
    out_file = tmp_path / "pretty.jsonl"
    h = JsonEventHandler(file_path=str(out_file), pretty=True)
    bus = EventBus(h)

    bus.process("x")

    raw = out_file.read_text(encoding="utf-8")
    # 'pretty' debe generar múltiples líneas por objeto (indentación)
    assert "\n" in raw
    # JSON válido al completo
    data = json.loads(raw)
    assert data["name"] == "x"
    assert data["count"] == 1