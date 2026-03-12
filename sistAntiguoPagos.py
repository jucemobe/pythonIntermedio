# -*- coding: utf-8 -*-
"""
Demostración de Patrón Adaptador en Python + Tests unitarios
============================================================

Incluye:
1) Adaptador CSV -> JSON
   - Versión funcional: adaptador_csv_a_json(path)
   - Versión con clases: LectorCSV + AdaptadorCSVaJSON

2) Sistema de pagos legado: PagosViejos
   - Adaptadores:
       * AdaptadorPagosViejosAJSON: imprime y devuelve dict (para JSON)
       * AdaptadorPagosViejosAJSONString: imprime y devuelve str JSON

3) Demos ejecutables (no fallan si falta test.csv)

4) Tests unitarios con unittest para:
   - Adaptadores de pagos
   - Adaptadores CSV -> JSON (funcional y OO)
"""

import csv
import json
import pathlib
from datetime import datetime
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# 1) ADAPTADOR CSV -> JSON
# ---------------------------------------------------------------------------

def adaptador_csv_a_json(path: pathlib.Path) -> List[str]:
    """
    Adaptador funcional que convierte un CSV a una lista de JSON strings.
    - Lee el CSV usando DictReader (cada fila es un dict).
    - Devuelve una lista de strings JSON (uno por fila).
    """
    with open(path, newline="", encoding="utf-8") as archivo:
        data = list(csv.DictReader(archivo))
    return [json.dumps(data_dict, ensure_ascii=False) for data_dict in data]


class LectorCSV:
    """Componente 'legado' o de bajo nivel que solo lee CSV a lista de dicts."""
    @staticmethod
    def leer(path: pathlib.Path) -> List[Dict[str, Any]]:
        with open(path, newline="", encoding="utf-8") as archivo:
            return list(csv.DictReader(archivo))


class AdaptadorCSVaJSON:
    """
    Adaptador orientado a objetos que toma lo leído por LectorCSV
    y lo convierte a lista de JSON strings.
    """
    def __init__(self):
        self.lector = LectorCSV()

    def adaptar(self, path: pathlib.Path) -> List[str]:
        data = self.lector.leer(path)
        return [json.dumps(data_dict, ensure_ascii=False) for data_dict in data]


# ---------------------------------------------------------------------------
# 2) SISTEMA ANTIGUO DE PAGOS + ADAPTADORES
# ---------------------------------------------------------------------------

class PagosViejos:
    """
    Sistema legado. Su interfaz es fija y devuelve un TEXTO legible.
    No debemos modificarlo; lo envolveremos con un adaptador.
    """
    def hacer_pago(self, monto: float, moneda: str) -> str:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Pago realizado: {monto:.2f} {moneda} a las {fecha}"


class AdaptadorPagosViejosAJSON:
    """
    Adaptador que:
      - Llama al sistema legado para obtener el TEXTO (comportamiento antiguo)
      - Imprime ese texto (requisito)
      - Devuelve además un dict con la información para JSON (valor añadido)
    """
    def __init__(self, sistema_legado: PagosViejos):
        self._legado = sistema_legado

    def hacer_pago(self, monto: float, moneda: str) -> Dict[str, Any]:
        # 1) Usamos el sistema viejo
        texto = self._legado.hacer_pago(monto, moneda)

        # 2) Mantener el comportamiento visible (print)
        print(texto)

        # 3) Mapear a estructura JSON (dict)
        return {
            "ok": True,
            "monto": float(monto),
            "moneda": moneda,
            "mensaje": texto
            # Puedes añadir más metadatos: id_transaccion, timestamp, etc.
        }


class AdaptadorPagosViejosAJSONString:
    """
    Variante del adaptador que en lugar de dict devuelve directamente
    un string JSON (por si lo quieres listo para enviar por red).
    También imprime el mensaje legado.
    """
    def __init__(self, sistema_legado: PagosViejos):
        self._legado = sistema_legado

    def hacer_pago(self, monto: float, moneda: str) -> str:
        texto = self._legado.hacer_pago(monto, moneda)
        print(texto)  # Imprime salida humana (requisito)
        payload = {
            "ok": True,
            "monto": float(monto),
            "moneda": moneda,
            "mensaje": texto
        }
        return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 3) DEMOS (opcionales)
# ---------------------------------------------------------------------------

def demo_csv():
    """
    Demostración de ambos adaptadores CSV -> JSON.
    Si no existe test.csv, informa y no falla el programa.
    """
    print("\n--- DEMO CSV -> JSON ---")
    p = pathlib.Path("test.csv")
    if not p.exists():
        print("No se encontró 'test.csv'. Crea un CSV de prueba para ver la demo.\n"
              "Ejemplo de contenido:\n"
              "nombre,edad,ciudad\n"
              "Ana,30,Madrid\n"
              "Luis,25,Sevilla\n")
        return

    # Versión funcional
    try:
        fila0_json = adaptador_csv_a_json(p)[0]
        print("[Funcional] Primera fila como JSON:", fila0_json)
    except Exception as e:
        print("Error en adaptador funcional CSV -> JSON:", e)

    # Versión con clases
    try:
        adapt = AdaptadorCSVaJSON()
        lista_json = adapt.adaptar(p)
        print("[OO] Lista completa JSON:")
        for s in lista_json:
            print("  ", s)
    except Exception as e:
        print("Error en adaptador OO CSV -> JSON:", e)


def demo_pagos():
    """
    Demostración del adaptador de pagos.
    Muestra impresión del mensaje legado y el JSON generado.
    """
    print("\n--- DEMO PAGOS LEGADO -> JSON ---")
    viejo = PagosViejos()

    # Adaptador que devuelve dict (recomendado si luego serializas tú)
    adapt_dict = AdaptadorPagosViejosAJSON(viejo)
    salida_dict = adapt_dict.hacer_pago(125.5, "EUR")
    print("JSON (dict) ->")
    print(json.dumps(salida_dict, ensure_ascii=False, indent=2))

    # Adaptador que ya devuelve un string JSON
    adapt_str = AdaptadorPagosViejosAJSONString(viejo)
    salida_str = adapt_str.hacer_pago(89.99, "USD")
    print("JSON (string) ->")
    print(salida_str)


# ---------------------------------------------------------------------------
# 4) TESTS UNITARIOS (unittest)
# ---------------------------------------------------------------------------

import io
import re
import os
import tempfile
import unittest
from contextlib import redirect_stdout


class TestAdaptadorCSV(unittest.TestCase):
    """
    Tests para:
      - adaptador_csv_a_json (funcional)
      - AdaptadorCSVaJSON (orientado a objetos)
    """

    def setUp(self):
        # Construimos un CSV temporal con encabezados y 2 filas
        self.tmpdir = tempfile.TemporaryDirectory()
        self.csv_path = pathlib.Path(self.tmpdir.name) / "datos.csv"
        contenido = (
            "nombre,edad,ciudad\n"
            "Ana,30,Madrid\n"
            "Luis,25,Sevilla\n"
        )
        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            f.write(contenido)

        # Estructuras esperadas (como dicts) para comparar tras parsear JSON
        self.esperado = [
            {"nombre": "Ana", "edad": "30", "ciudad": "Madrid"},
            {"nombre": "Luis", "edad": "25", "ciudad": "Sevilla"},
        ]

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_funcional_devuelve_lista_de_json_strings(self):
        salida = adaptador_csv_a_json(self.csv_path)
        self.assertIsInstance(salida, list)
        self.assertEqual(len(salida), 2)
        # Cada elemento debe ser un string JSON válido que al parsear coincida
        filas = [json.loads(s) for s in salida]
        self.assertEqual(filas, self.esperado)

    def test_oo_devuelve_lista_de_json_strings(self):
        adapt = AdaptadorCSVaJSON()
        salida = adapt.adaptar(self.csv_path)
        self.assertIsInstance(salida, list)
        self.assertEqual(len(salida), 2)
        filas = [json.loads(s) for s in salida]
        self.assertEqual(filas, self.esperado)

    def test_csv_con_espacios_y_caracteres_especiales(self):
        # Creamos otro CSV con caracteres Unicode y espacios en campos
        csv_path2 = pathlib.Path(self.tmpdir.name) / "datos_utf8.csv"
        contenido = (
            "nombre,comentario\n"
            "Marta,¡Hola mundo!\n"
            "José Luis,\"Texto con, coma\"\n"
        )
        with open(csv_path2, "w", encoding="utf-8", newline="") as f:
            f.write(contenido)

        # Funcional
        salida_f = adaptador_csv_a_json(csv_path2)
        filas_f = [json.loads(s) for s in salida_f]
        self.assertEqual(
            filas_f,
            [
                {"nombre": "Marta", "comentario": "¡Hola mundo!"},
                {"nombre": "José Luis", "comentario": "Texto con, coma"},
            ],
        )

        # OO
        salida_oo = AdaptadorCSVaJSON().adaptar(csv_path2)
        filas_oo = [json.loads(s) for s in salida_oo]
        self.assertEqual(filas_oo, filas_f)

    def test_csv_vacio_devuelve_lista_vacia(self):
        csv_vacio = pathlib.Path(self.tmpdir.name) / "vacio.csv"
        with open(csv_vacio, "w", encoding="utf-8", newline="") as f:
            f.write("")  # sin encabezados ni filas

        # Ambos deben devolver lista vacía (DictReader sin encabezados => 0 filas)
        self.assertEqual(adaptador_csv_a_json(csv_vacio), [])
        self.assertEqual(AdaptadorCSVaJSON().adaptar(csv_vacio), [])

    def test_csv_solo_encabezados_devuelve_lista_vacia(self):
        csv_headers = pathlib.Path(self.tmpdir.name) / "headers.csv"
        with open(csv_headers, "w", encoding="utf-8", newline="") as f:
            f.write("a,b,c\n")
        self.assertEqual(adaptador_csv_a_json(csv_headers), [])
        self.assertEqual(AdaptadorCSVaJSON().adaptar(csv_headers), [])

    def test_errores_archivo_inexistente(self):
        ruta_inexistente = pathlib.Path(self.tmpdir.name) / "noexiste.csv"
        with self.assertRaises(FileNotFoundError):
            _ = adaptador_csv_a_json(ruta_inexistente)
        with self.assertRaises(FileNotFoundError):
            _ = AdaptadorCSVaJSON().adaptar(ruta_inexistente)


class TestAdaptadorPagos(unittest.TestCase):
    """
    Tests del adaptador de pagos (como ya te mostré).
    """

    def setUp(self):
        self.legado = PagosViejos()

    def test_adaptador_dict_imprime_y_devuelve_estructura(self):
        adapt = AdaptadorPagosViejosAJSON(self.legado)

        buf = io.StringIO()
        with redirect_stdout(buf):
            result = adapt.hacer_pago(100.0, "EUR")

        # Verifica impresión
        output = buf.getvalue()
        self.assertIn("Pago realizado", output)
        self.assertIn("100.00 EUR", output)
        self.assertRegex(output, r"a las \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

        # Verifica estructura devuelta (dict)
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("ok"))
        self.assertEqual(result.get("monto"), 100.0)
        self.assertEqual(result.get("moneda"), "EUR")
        self.assertIn("mensaje", result)
        self.assertIn("100.00 EUR", result["mensaje"])

    def test_adaptador_str_json_imprime_y_devuelve_json_string_valido(self):
        adapt = AdaptadorPagosViejosAJSONString(self.legado)

        buf = io.StringIO()
        with redirect_stdout(buf):
            json_str = adapt.hacer_pago(50, "USD")

        # Verifica impresión
        output = buf.getvalue()
        self.assertIn("Pago realizado", output)
        self.assertIn("50.00 USD", output)

        # Verifica que lo devuelto es un JSON válido con claves esperadas
        try:
            payload = json.loads(json_str)
        except json.JSONDecodeError:
            self.fail("El adaptador no devolvió un JSON válido")

        self.assertIsInstance(payload, dict)
        self.assertTrue(payload.get("ok"))
        self.assertEqual(payload.get("monto"), 50.0)
        self.assertEqual(payload.get("moneda"), "USD")
        self.assertIn("mensaje", payload)
        self.assertIn("50.00 USD", payload["mensaje"])

    def test_no_modifica_interfaz_legado(self):
        """
        Asegura que la clase legado sigue respondiendo con el mismo contrato:
        - método hacer_pago
        - devuelve un string legible
        """
        texto = self.legado.hacer_pago(12.34, "EUR")
        self.assertIsInstance(texto, str)
        self.assertIn("Pago realizado", texto)
        self.assertIn("12.34 EUR", texto)

    def test_montos_y_monedas_varias(self):
        """
        Prueba varios pares (monto, moneda) para el adaptador dict.
        No comprobamos la fecha exacta, solo que el mensaje y los datos
        son coherentes.
        """
        adapt = AdaptadorPagosViejosAJSON(self.legado)
        casos = [
            (1, "EUR"),
            (9999.99, "USD"),
            (0.5, "JPY"),
        ]
        for monto, moneda in casos:
            buf = io.StringIO()
            with redirect_stdout(buf):
                data = adapt.hacer_pago(monto, moneda)
            out = buf.getvalue()
            # Impresión coherente
            self.assertIn("Pago realizado", out)
            self.assertIn(f"{monto:.2f} {moneda}", out)
            # Dict coherente
            self.assertEqual(data["monto"], float(monto))
            self.assertEqual(data["moneda"], moneda)
            self.assertIn(f"{monto:.2f} {moneda}", data["mensaje"])

    def test_formato_mensaje(self):
        """
        Verifica que el mensaje guarda el formato general esperado:
        'Pago realizado: <monto> <moneda> a las <YYYY-MM-DD HH:MM:SS>'
        """
        texto = self.legado.hacer_pago(7, "EUR")
        patron = r"^Pago realizado: \d+\.\d{2} [A-Z]{3} a las \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        self.assertRegex(texto, patron)


# ---------------------------------------------------------------------------
# 5) ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Demos
    demo_csv()
    demo_pagos()

    # Sugerencia: para ejecutar tests:
    #   python -m unittest main -v
    # o con pytest:
    #   pytest -q