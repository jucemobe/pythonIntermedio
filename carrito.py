from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional
import re
import uuid
from datetime import datetime


# -------------------------------------------------------------------
# Utilidades de carrito basado en diccionario { item: (cantidad, precio) }
# -------------------------------------------------------------------
def validar_carrito(cart: Dict[str, Tuple[int, float]]) -> None:
    if cart is None or not isinstance(cart, dict) or len(cart) == 0:
        raise ValueError("El carrito está vacío o no es un diccionario válido.")
    for item, tupla in cart.items():
        if (not isinstance(tupla, tuple)) or len(tupla) != 2:
            raise ValueError(f"El ítem '{item}' debe mapear a una tupla (cantidad, precio).")
        qty, price = tupla
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError(f"Cantidad inválida para '{item}': {qty}")
        if not (isinstance(price, int) or isinstance(price, float)) or price < 0:
            raise ValueError(f"Precio inválido para '{item}': {price}")


def total_carrito(cart: Dict[str, Tuple[int, float]]) -> float:
    validar_carrito(cart)
    total = 0.0
    for item, (qty, price) in cart.items():
        total += qty * price
    return round(total, 2)


def imprimir_carrito(cart: Dict[str, Tuple[int, float]], currency: str = "EUR") -> None:
    print("=== Carrito ===")
    for item, (qty, price) in cart.items():
        subtotal = round(qty * price, 2)
        print(f"- {item}: {qty} x {price:.2f} {currency} = {subtotal:.2f} {currency}")
    print(f"TOTAL: {total_carrito(cart):.2f} {currency}")
    print()


# -------------------------------------------------------------------
# Resultados y estados de pago
# -------------------------------------------------------------------
class PaymentStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


@dataclass
class PaymentResult:
    status: PaymentStatus
    transaction_id: Optional[str]
    message: str


# -------------------------------------------------------------------
# Enmascarado sencillo para prints
# -------------------------------------------------------------------
def mask_phone(phone: str) -> str:
    # Deja últimos 3 visibles
    return "*" * max(0, len(phone) - 3) + phone[-3:]


def mask_email(email: str) -> str:
    try:
        local, domain = email.split("@")
    except ValueError:
        return "***"
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_card(number: str) -> str:
    digits = number.replace(" ", "")
    return "*" * max(0, len(digits) - 4) + digits[-4:]


def mask_cvv(cvv: str) -> str:
    return "*" * len(cvv)


# -------------------------------------------------------------------
# Métodos de pago (simulados) con prints de inputs
# -------------------------------------------------------------------
class BizumPayment:
    PHONE_REGEX = re.compile(r"^\+?\d{9,15}$")

    def __init__(self, phone: str):
        if not phone or not self.PHONE_REGEX.match(phone):
            raise ValueError("Número de teléfono Bizum inválido.")
        self.phone = phone

    def pay(self, amount: float, currency: str = "EUR") -> PaymentResult:
        print(">>> Pago con BIZUM")
        print(f"    Input -> phone: {mask_phone(self.phone)}")
        print(f"    Importe: {amount:.2f} {currency}")

        if amount <= 0:
            raise ValueError("El importe debe ser mayor que 0.")

        # Regla simulada: aprueba si el último dígito del teléfono es par
        try:
            approved = int(self.phone[-1]) % 2 == 0
        except ValueError:
            approved = False

        if approved:
            tx = str(uuid.uuid4())
            print("    Resultado: SUCCESS")
            print(f"    transaction_id: {tx}")
            print("    Mensaje: Bizum aprobado\n")
            return PaymentResult(PaymentStatus.SUCCESS, tx, "Bizum aprobado")
        else:
            print("    Resultado: FAILED")
            print("    transaction_id: None")
            print("    Mensaje: Bizum denegado por el emisor\n")
            return PaymentResult(PaymentStatus.FAILED, None, "Bizum denegado por el emisor")


class CreditCardPayment:
    CARD_REGEX = re.compile(r"^\d{13,19}$")
    CVV_REGEX = re.compile(r"^\d{3,4}$")
    EXP_REGEX = re.compile(r"^(0[1-9]|1[0-2])\/(\d{2})$")  # MM/YY

    def __init__(self, number: str, expiry_mm_yy: str, cvv: str, holder_name: Optional[str] = None):
        digits = number.replace(" ", "")
        if not self.CARD_REGEX.match(digits):
            raise ValueError("Número de tarjeta inválido.")
        if not self.EXP_REGEX.match(expiry_mm_yy):
            raise ValueError("Fecha de caducidad inválida. Use MM/YY.")
        if not self.CVV_REGEX.match(cvv):
            raise ValueError("CVV inválido.")
        self.number = digits
        self.expiry = expiry_mm_yy
        self.cvv = cvv
        self.holder = holder_name
        self._validate_not_expired()

    def _validate_not_expired(self):
        mm, yy = self.expiry.split("/")
        exp_month = int(mm)
        exp_year = 2000 + int(yy)
        now = datetime.now()
        # Consideramos vencida si el mes ya pasó
        if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
            raise ValueError("La tarjeta está caducada.")

    def pay(self, amount: float, currency: str = "EUR") -> PaymentResult:
        print(">>> Pago con TARJETA")
        print(f"    Input -> number: {mask_card(self.number)} | expiry: {self.expiry} | cvv: {mask_cvv(self.cvv)} | holder: {self.holder or '-'}")
        print(f"    Importe: {amount:.2f} {currency}")

        if amount <= 0:
            raise ValueError("El importe debe ser mayor que 0.")

        # Regla simulada: aprueba si el último dígito de la tarjeta es par
        approved = int(self.number[-1]) % 2 == 0

        if approved:
            tx = str(uuid.uuid4())
            print("    Resultado: SUCCESS")
            print(f"    transaction_id: {tx}")
            print("    Mensaje: Tarjeta aprobada\n")
            return PaymentResult(PaymentStatus.SUCCESS, tx, "Tarjeta aprobada")
        else:
            print("    Resultado: FAILED")
            print("    transaction_id: None")
            print("    Mensaje: Tarjeta denegada por la entidad\n")
            return PaymentResult(PaymentStatus.FAILED, None, "Tarjeta denegada por la entidad")


class PayPalPayment:
    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, email: str, password: str):
        if not self.EMAIL_REGEX.match(email):
            raise ValueError("Correo de PayPal inválido.")
        if not password or len(password) < 6:
            raise ValueError("Contraseña de PayPal demasiado corta.")
        self.email = email
        self.password = password  # En un sistema real no se imprimiría ni guardaría en claro

    def pay(self, amount: float, currency: str = "EUR") -> PaymentResult:
        print(">>> Pago con PAYPAL")
        print(f"    Input -> email: {mask_email(self.email)} | password: {'*' * len(self.password)}")
        print(f"    Importe: {amount:.2f} {currency}")

        if amount <= 0:
            raise ValueError("El importe debe ser mayor que 0.")

        # Regla simulada: aprueba si la parte local del email tiene > 3 caracteres
        local = self.email.split("@")[0]
        approved = len(local) > 3

        if approved:
            tx = str(uuid.uuid4())
            print("    Resultado: SUCCESS")
            print(f"    transaction_id: {tx}")
            print("    Mensaje: PayPal aprobado\n")
            return PaymentResult(PaymentStatus.SUCCESS, tx, "PayPal aprobado")
        else:
            print("    Resultado: FAILED")
            print("    transaction_id: None")
            print("    Mensaje: PayPal rechazado por credenciales\n")
            return PaymentResult(PaymentStatus.FAILED, None, "PayPal rechazado por credenciales")


class CashPayment:
    def pay(self, amount: float, currency: str = "EUR") -> PaymentResult:
        print(">>> Pago AL CONTADO (efectivo)")
        print("    Input -> sin credenciales (marcar como pendiente)")
        print(f"    Importe: {amount:.2f} {currency}")

        if amount <= 0:
            raise ValueError("El importe debe ser mayor que 0.")

        tx = str(uuid.uuid4())
        print("    Resultado: PENDING")
        print(f"    transaction_id: {tx}")
        print("    Mensaje: Pago en efectivo pendiente de cobro\n")
        return PaymentResult(PaymentStatus.PENDING, tx, "Pago en efectivo pendiente de cobro")

def comprobar_resultado(carrito, metodo_nombre, resultado):
    print("=== COMPROBACIÓN ===")
    
    esperado = total_carrito(carrito)
    print(f"Total esperado del carrito: {esperado:.2f} EUR")
    print(f"Método de pago: {metodo_nombre}")
    print(f"Estado del pago: {resultado.status.value}")
    print(f"transaction_id: {resultado.transaction_id}")
    print(f"Mensaje: {resultado.message}")

    ok = True

    # 1. total correcto
    if esperado <= 0:
        ok = False
        print("❌ ERROR: El total del carrito no es válido")

    # 2. estado permitido
    if resultado.status not in (PaymentStatus.SUCCESS, PaymentStatus.PENDING):
        ok = False
        print("❌ ERROR: El pago ha sido rechazado")
    else:
        print("✔️ Estado del pago aceptable")

    # 3. transaction_id correcto
    if resultado.status == PaymentStatus.SUCCESS and resultado.transaction_id is None:
        ok = False
        print("❌ ERROR: Pago SUCCESS pero sin transaction_id")
    if resultado.status == PaymentStatus.PENDING and resultado.transaction_id is None:
        ok = False
        print("❌ ERROR: Pago PENDING pero sin transaction_id")
    if resultado.status == PaymentStatus.FAILED and resultado.transaction_id is not None:
        ok = False
        print("❌ ERROR: Pago FAILED pero con transaction_id")

    if ok:
        print("🎉 COMPROBACIÓN FINAL: TODO CORRECTO\n")
    else:
        print("⚠️ COMPROBACIÓN FINAL: ALGÚN ERROR DETECTADO\n")

# -------------------------------------------------------------------
# Orquestador
# -------------------------------------------------------------------
def procesar_pago(cart: Dict[str, Tuple[int, float]], metodo, currency: str = "EUR") -> PaymentResult:
    imprimir_carrito(cart, currency)
    amount = total_carrito(cart)
    return metodo.pay(amount, currency)


# -------------------------------------------------------------------
# Ejemplos de uso y DEMO con prints
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Ejemplo 1: Carrito simple (como tu ejemplo de huevos)
    carrito1 = {
        "huevos": (2, 0.55),  # total 1.10
    }

    # Ejemplo 2: Carrito con varios productos
    carrito2 = {
        "camiseta": (2, 19.99),
        "pantalon": (1, 39.99),
        "calcetines": (3, 2.50),
    }

print("\n===== DEMO: BIZUM =====")
bizum = BizumPayment(phone="+34600111222")
resultado = procesar_pago(carrito1, bizum)
comprobar_resultado(carrito1, "BIZUM", resultado)

print("\n===== DEMO: TARJETA =====")
tarjeta = CreditCardPayment(number="4111111111111112", expiry_mm_yy="12/29", cvv="123", holder_name="Cliente Demo")
resultado = procesar_pago(carrito2, tarjeta)
comprobar_resultado(carrito2, "TARJETA", resultado)

print("\n===== DEMO: PAYPAL =====")
paypal = PayPalPayment(email="cliente.demo@example.com", password="secreto123")
resultado = procesar_pago(carrito2, paypal)
comprobar_resultado(carrito2, "PAYPAL", resultado)

print("\n===== DEMO: AL CONTADO =====")
contado = CashPayment()
resultado = procesar_pago(carrito1, contado)
comprobar_resultado(carrito1, "CONTADO", resultado)