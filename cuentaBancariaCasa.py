class CuentaBancaria:
    """
    Cuenta bancaria con saldo derivado a partir de un histórico de transacciones.
    
    Reglas:
    - El saldo es la suma de todas las transacciones (no se almacena directamente).
    - depositar(cantidad): agrega un movimiento positivo (+cantidad). No se permiten cantidades <= 0.
    - retirar(cantidad): agrega un movimiento negativo (-cantidad). No se permiten cantidades <= 0,
      ni retirar más que el saldo disponible (no se admite saldo negativo).
    - ultimo_movimiento: último movimiento registrado, o 0 si no hay movimientos.
    - No se puede asignar saldo directamente (setter deshabilitado).
    - Al imprimir, muestra: "Cuenta de <titular> - saldo: <total>".
    """

    def __init__(self, titular: str):
        if not isinstance(titular, str) or not titular.strip():
            raise ValueError("El titular debe ser un string no vacío.")
        self._titular = titular.strip()
        self._movimientos = []  # lista de ints/floats: +depósitos, -retiros

    # ------------- Utilidades internas -------------
    @staticmethod
    def _es_numero_real(x):
        # Aceptar int/float como números reales; excluir bool explícitamente.
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def _validar_cantidad_positiva(self, cantidad):
        if not self._es_numero_real(cantidad):
            raise TypeError("La cantidad debe ser un número (int o float).")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")

    # ------------- API pública -------------
    def depositar(self, cantidad):
        """
        Deposita 'cantidad' en la cuenta y registra el movimiento positivo.
        """
        self._validar_cantidad_positiva(cantidad)
        self._movimientos.append(+float(cantidad))

    def retirar(self, cantidad):
        """
        Retira 'cantidad' de la cuenta y registra el movimiento negativo.
        No permite que el saldo quede en negativo.
        """
        self._validar_cantidad_positiva(cantidad)
        if cantidad > self.saldo:
            raise ValueError(
                f"No se puede retirar {cantidad}: saldo insuficiente ({self.saldo})."
            )
        self._movimientos.append(-float(cantidad))

    @property
    def saldo(self):
        """
        Saldo derivado: suma de todos los movimientos.
        """
        # Usamos sum() sobre la lista; saldo no se guarda directamente.
        return sum(self._movimientos) if self._movimientos else 0.0

    @saldo.setter
    def saldo(self, _):
        """
        El saldo no se puede modificar directamente.
        """
        raise AttributeError("El saldo es derivado y no se puede asignar directamente.")

    @property
    def ultimo_movimiento(self):
        """
        Devuelve el último movimiento (+depósito o -retiro), o 0 si no existe ninguno.
        """
        if not self._movimientos:
            return 0
        return self._movimientos[-1]

    @property
    def titular(self):
        return self._titular

    def __str__(self):
        # Mostrar saldo sin muchos decimales molestos:
        saldo_fmt = int(self.saldo) if float(self.saldo).is_integer() else round(self.saldo, 2)
        return f"Cuenta de {self._titular} - saldo: {saldo_fmt}"


# =======================
# EJEMPLO DE USO
# =======================
if __name__ == "__main__":
    cuenta = CuentaBancaria("Joaquin")
    cuenta.depositar(100)
    cuenta.retirar(20)
    print(cuenta.saldo)              # Debería ser 80
    print(cuenta.ultimo_movimiento)  # Debería ser -20
    print(cuenta)                    # "Cuenta de Joaquin - saldo: 80"
    try:
        cuenta.saldo = 1000          # NO SE PUEDE HACER
    except AttributeError as e:
        print("OK:", e)

    # Pruebas adicionales:
    # cuenta.depositar(-5)           # ValueError
    # cuenta.retirar(1000)          # ValueError por saldo insuficiente
    # cuenta.depositar(True)        # TypeError (bool no permitido)