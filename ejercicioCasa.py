# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation
from typing import List, Union

Numero = Union[int, float, Decimal]


class CuentaBancaria:
    """
    Cuenta bancaria con saldo derivado de su histórico de transacciones.

    - No almacena un saldo fijo; lo calcula sumando las transacciones.
    - depositar(cantidad): registra +cantidad (cantidad debe ser > 0).
    - retirar(cantidad): registra -cantidad si hay saldo suficiente (evita saldo negativo).
    - saldo (property): suma de transacciones (solo lectura).
    - ultimo_movimiento (property): último movimiento registrado o 0 si no hay.
    - Impresión: "Cuenta de <titular> - saldo: <total>"
    """

    def __init__(self, titular: str):
        self.titular = str(titular).strip() or "Titular"
        self._transacciones: List[Decimal] = []

    # ---------------------------
    # Utilidades internas
    # ---------------------------
    @staticmethod
    def _to_decimal(valor: Numero) -> Decimal:
        """Convierte a Decimal de forma segura."""
        if isinstance(valor, Decimal):
            return valor
        try:
            return Decimal(str(valor))
        except (InvalidOperation, ValueError, TypeError):
            raise TypeError("La cantidad debe ser un número (int, float o Decimal).")

    def _validar_positiva(self, cantidad: Decimal) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")

    # ---------------------------
    # API de negocio
    # ---------------------------
    def depositar(self, cantidad: Numero) -> None:
        """Registra un depósito (+cantidad)."""
        cantidad_dec = self._to_decimal(cantidad)
        self._validar_positiva(cantidad_dec)
        self._transacciones.append(cantidad_dec)
        print(f"[INFO] Depósito de {cantidad_dec} registrado. Saldo actual: {self.saldo}")

    def retirar(self, cantidad: Numero) -> None:
        """Registra un retiro (-cantidad) si hay saldo suficiente (no permite saldo negativo)."""
        cantidad_dec = self._to_decimal(cantidad)
        self._validar_positiva(cantidad_dec)

        if cantidad_dec > self.saldo:
            raise ValueError(
                f"No se puede retirar {cantidad_dec}: saldo insuficiente ({self.saldo})."
            )

        self._transacciones.append(-cantidad_dec)
        print(f"[INFO] Retiro de {cantidad_dec} registrado. Saldo actual: {self.saldo}")

    # ---------------------------
    # Propiedades
    # ---------------------------
    @property
    def saldo(self) -> Decimal:
        """Saldo derivado (suma de transacciones). Solo lectura."""
        return sum(self._transacciones, start=Decimal("0"))

    @saldo.setter
    def saldo(self, _):
        """Bloquea la modificación directa del saldo."""
        raise AttributeError("El saldo no se puede modificar directamente. Use depositar/retirar.")

    @property
    def ultimo_movimiento(self) -> Decimal:
        """Último movimiento (+depósito / -retiro) o 0 si no existe."""
        if not self._transacciones:
            return Decimal("0")
        return self._transacciones[-1]

    @property
    def historico(self) -> List[Decimal]:
        """
        Devuelve una copia inmutable (shallow) del histórico para consulta.
        Los valores son Decimals, p.ej. [+30, -20, ...]
        """
        return list(self._transacciones)

    # ---------------------------
    # Representaciones
    # ---------------------------
    def __str__(self) -> str:
        return f"Cuenta de {self.titular} - saldo: {self.saldo}"

    def __repr__(self) -> str:
        return f"CuentaBancaria(titular={self.titular!r}, saldo={self.saldo}, movimientos={len(self._transacciones)})"


# ============================
# Ejemplo de uso / Pruebas rápidas
# ============================
if __name__ == "__main__":
    cuenta = CuentaBancaria("Joaquin")
    cuenta.depositar(100)
    cuenta.retirar(20)
    print(cuenta.saldo)               # Debería ser 80
    print(cuenta.ultimo_movimiento)   # Debería ser -20
    print(cuenta)                     # "Cuenta de Joaquin - saldo: 80"

    # No se puede asignar saldo directamente
    try:
        cuenta.saldo = 1000           # Debe fallar
    except Exception as e:
        print("[ERROR]", e)

    # No se puede retirar más de lo disponible
    try:
        cuenta.retirar(1000)          # Debe fallar por saldo insuficiente
    except Exception as e:
        print("[ERROR]", e)

    # No se aceptan depósitos/ Retiros con cantidad no positiva
    for c in (0, -10):
        try:
            cuenta.depositar(c)
        except Exception as e:
            print("[ERROR depositar]", e)
        try:
            cuenta.retirar(c)
        except Exception as e:
            print("[ERROR retirar]", e)