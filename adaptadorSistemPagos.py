from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Dict, Any
import json
import re


# === Sistema legado ===
class PagosViejos:
    def hacer_pago(self, monto: float, moneda: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Pagado {monto} {moneda} el {timestamp}"


# === Interfaz objetivo ===
class ProveedorPagos(Protocol):
    def pagar(self, monto: float, moneda: str) -> Dict[str, Any]:
        ...


# === Adaptador con comprensión de diccionario ===
@dataclass
class PagoAdapter(ProveedorPagos):
    legado: PagosViejos

    def pagar(self, monto: float, moneda: str) -> Dict[str, Any]:
        resultado_texto = self.legado.hacer_pago(monto, moneda)

        patron = (
            r"Pagado\s+([0-9]+(?:[.,][0-9]+)?)\s+([A-Za-z]{3})\s+el\s+"
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
        )
        m = re.search(patron, resultado_texto)

        if m:
            monto_str, moneda_match, fecha_hora = m.groups()
            monto_norm = float(monto_str.replace(",", "."))
            # Pares clave-valor a partir de los datos parseados
            items = [
                ("status", "ok"),
                ("monto", monto_norm),
                ("moneda", moneda_match.upper()),
                ("fecha_hora", fecha_hora),
                ("fuente", "PagosViejos"),
                ("mensaje_original", resultado_texto),
                ("parseado", True),
            ]
        else:
            # Si el formato no coincide, devolvemos valores razonables
            items = [
                ("status", "ok"),
                ("monto", float(str(monto).replace(",", "."))),
                ("moneda", moneda.upper()),
                ("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ("fuente", "PagosViejos"),
                ("mensaje_original", resultado_texto),
                ("parseado", False),
            ]

        # --- Comprensión de diccionario ---
        info = {k: v for (k, v) in items}

        # Print con la información solicitada
        print(f"[PAGO] {info['monto']} {info['moneda']} a las {info['fecha_hora']} (fuente: {info['fuente']})")

        return info


# === Ejemplo de uso ===
if __name__ == "__main__":
    pagos_viejos = PagosViejos()
    adaptador = PagoAdapter(legado=pagos_viejos)

    resultado = adaptador.pagar(149.99, "eur")

    # Si necesitas el JSON serializado como texto:
    resultado_json = json.dumps(resultado, ensure_ascii=False)
    print("JSON:", resultado_json)