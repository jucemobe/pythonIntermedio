# -*- coding: utf-8 -*-

from decimal import Decimal, InvalidOperation
from typing import Union, Optional

Number = Union[int, float, Decimal]


class Item:
    """
    Clase de un ítem de ecommerce con precio validado:
      - El precio se maneja como número (Decimal internamente).
      - Al asignar un precio, debe ser estrictamente positivo (> 0).
      - Al imprimir el ítem, el precio se muestra como texto con su moneda.
      - Muestra un mensaje al cambiar el precio o al eliminarlo.
      - Al eliminar el precio, no desaparece: se setea a 0 (soft delete).
    """

    def __init__(self, nombre: str, precio: Number, moneda: str = "€", decimales: int = 2):
        self.nombre = str(nombre).strip() or "Item"
        self.moneda = moneda
        self.decimales = int(decimales) if decimales is not None else 2
        self._precio: Optional[Decimal] = None  # almacenado como Decimal
        # usar el setter para validar y emitir mensaje inicial
        self.precio = precio

    # ---------------------------
    # Utilidades internas
    # ---------------------------
    @staticmethod
    def _a_decimal(valor: Number) -> Decimal:
        """Convierte int/float/Decimal a Decimal de forma segura."""
        if isinstance(valor, Decimal):
            return valor
        try:
            # str() evita issues de representación binaria de float
            return Decimal(str(valor))
        except (InvalidOperation, ValueError, TypeError):
            raise TypeError("El precio debe ser un número (int, float o Decimal).")

    def _formatear_moneda(self, cantidad: Decimal) -> str:
        """
        Devuelve la cantidad formateada como texto con separador decimal
        estilo español (coma para decimales) y la unidad monetaria.
        """
        q = cantidad.quantize(Decimal((0, (1,), -self.decimales))) if self.decimales >= 0 else cantidad
        # Formateo básico con punto decimal y miles
        base = f"{q:,.{self.decimales}f}"
        # Adaptar a formato 'es' (coma decimal, punto de miles -> opcional)
        base = base.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{base} {self.moneda}"

    # ---------------------------
    # Propiedad precio
    # ---------------------------
    @property
    def precio(self) -> Decimal:
        """Devuelve el precio numérico (Decimal)."""
        return self._precio if self._precio is not None else Decimal("0")

    @precio.setter
    def precio(self, nuevo: Number) -> None:
        """
        Valida y asigna un nuevo precio:
          - Debe ser numérico
          - Debe ser > 0 (estrictamente positivo)
        Emite un mensaje si cambia el valor.
        """
        nuevo_dec = self._a_decimal(nuevo)

        if nuevo_dec <= 0:
            raise ValueError("El precio debe ser un número positivo mayor que 0.")

        anterior = self._precio
        self._precio = nuevo_dec

        if anterior is None:
            print(f"[INFO] Precio inicial de '{self.nombre}': {self._formatear_moneda(self._precio)}")
        elif anterior != nuevo_dec:
            print(
                f"[INFO] Precio de '{self.nombre}' cambiado: "
                f"{self._formatear_moneda(anterior)} -> {self._formatear_moneda(self._precio)}"
            )
        else:
            print(f"[INFO] Precio de '{self.nombre}' sin cambios: {self._formatear_moneda(self._precio)}")

    @precio.deleter
    def precio(self) -> None:
        """
        "Eliminar" el precio no lo elimina realmente:
        realiza un soft delete estableciéndolo a 0 y emite un mensaje.
        """
        anterior = self._precio if self._precio is not None else Decimal("0")
        self._precio = Decimal("0")
        print(
            f"[INFO] Precio de '{self.nombre}' eliminado (soft delete): "
            f"{self._formatear_moneda(anterior)} -> {self._formatear_moneda(self._precio)}"
        )

    # ---------------------------
    # Representaciones
    # ---------------------------
    def __str__(self) -> str:
        """Representación amigable con el precio en texto y su moneda."""
        return f"{self.nombre}: {self._formatear_moneda(self.precio)}"

    def __repr__(self) -> str:
        return f"Item(nombre={self.nombre!r}, precio={str(self.precio)}, moneda={self.moneda!r})"

    def __float__(self) -> float:
        """Permite convertir el precio a float cuando se necesite interoperar."""
        return float(self.precio)

    def __int__(self) -> int:
        """Conversión a int del precio (truncando)."""
        return int(self.precio)


# ============================
# Pruebas rápidas
# ============================
if __name__ == "__main__":
    # Crear ítem con precio inicial
    libro = Item("Libro Python", 19.99)           # [INFO] precio inicial
    print(libro)                                  # Libro Python: 19,99 €

    # Cambiar a un precio nuevo (válido)
    libro.precio = 24.5                           # [INFO] cambio
    print(libro)                                  # Libro Python: 24,50 €

    # Intento de asignar precio no positivo
    try:
        libro.precio = 0                          # debe fallar
    except Exception as e:
        print("[ERROR]", e)

    # Soft delete del precio → queda en 0 con mensaje
    del libro.precio                               # [INFO] eliminado -> 0
    print(libro)                                   # Libro Python: 0,00 €

    # Asignación posterior vuelve a validar normal
    libro.precio = 12.3
    print(float(libro))                            # interoperabilidad: 12.3