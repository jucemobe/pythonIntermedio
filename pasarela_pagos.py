from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional
import re
import uuid
from datetime import datetime

# =========================================
#    PASARELA DE PAGOS (INTERACTIVA)
# =========================================

# -----------------------------------------
# Registro histórico de pagos en memoria
# -----------------------------------------
HISTORIAL_PAGOS = []  # cada elemento es un dict con datos del pago


# -----------------------------------------
# Utilidades de carrito { item: (cant, precio) }
# -----------------------------------------
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


# -----------------------------------------
# Resultados y estados de pago
# -----------------------------------------
class PaymentStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


@dataclass
class PaymentResult:
    status: PaymentStatus
    transaction_id: Optional[str]
    message: str


# -----------------------------------------
# Enmascarado para prints
# -----------------------------------------
def mask_phone(phone: str) -> str:
    # Muestra últimos 3 dígitos
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


# -----------------------------------------
# Métodos de pago (simulados)
# -----------------------------------------
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


# -----------------------------------------
# Orquestador + comprobador + registro
# -----------------------------------------
def procesar_pago(cart: Dict[str, Tuple[int, float]], metodo, currency: str = "EUR") -> PaymentResult:
    imprimir_carrito(cart, currency)
    amount = total_carrito(cart)
    return metodo.pay(amount, currency)


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

    # 3. transaction_id coherente
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


def registrar_pago(carrito, metodo, resultado):
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "carrito": carrito.copy(),
        "metodo": metodo,
        "estado": resultado.status.value,
        "mensaje": resultado.message,
        "transaction_id": resultado.transaction_id,
        "total": total_carrito(carrito)
    }
    HISTORIAL_PAGOS.append(registro)


def ver_historial():
    print("\n=========== HISTÓRICO DE PAGOS ===========\n")
    if not HISTORIAL_PAGOS:
        print("No hay pagos registrados.\n")
        return

    for i, r in enumerate(HISTORIAL_PAGOS, start=1):
        print(f"Pago #{i}")
        print(f"Fecha: {r['fecha']}")
        print(f"Método: {r['metodo']}")
        print(f"Estado: {r['estado']}")
        print(f"Total: {r['total']:.2f} EUR")
        print(f"transaction_id: {r['transaction_id']}")
        print(f"Mensaje: {r['mensaje']}")
        print("Carrito usado:")
        for item, (qty, price) in r["carrito"].items():
            print(f"  - {item}: {qty} x {price:.2f} EUR")
        print("--------------------------------------\n")


# -----------------------------------------
# Helpers de entrada por consola
# -----------------------------------------
def leer_opcion(msg: str, opciones_validas) -> str:
    while True:
        op = input(msg).strip()
        if op in opciones_validas:
            return op
        print(f"Opción inválida. Válidas: {', '.join(sorted(opciones_validas))}")


def prompt_no_vacio(msg: str) -> str:
    while True:
        s = input(msg).strip()
        if s:
            return s
        print("No puede estar vacío.")


def prompt_int(msg: str, minimo: int = 1) -> int:
    while True:
        s = input(msg).strip()
        try:
            v = int(s)
            if v >= minimo:
                return v
            print(f"Debe ser >= {minimo}.")
        except ValueError:
            print("Introduce un número entero válido.")


def prompt_float(msg: str, minimo: float = 0.0) -> float:
    while True:
        s = input(msg).replace(",", ".").strip()
        try:
            v = float(s)
            if v >= minimo:
                return v
            print(f"Debe ser >= {minimo}.")
        except ValueError:
            print("Introduce un número válido (usa punto o coma para decimales).")


# -----------------------------------------
# Creación/elección de carritos
# -----------------------------------------
def crear_carrito_manual() -> Dict[str, Tuple[int, float]]:
    print("\n== Crear carrito manual ==")
    cart: Dict[str, Tuple[int, float]] = {}
    while True:
        nombre = input("Nombre del producto (ENTER para terminar): ").strip()
        if nombre == "":
            if len(cart) == 0:
                print("Añade al menos un producto.")
                continue
            break
        cantidad = prompt_int(f"Cantidad para '{nombre}': ", minimo=1)
        precio = prompt_float(f"Precio unitario para '{nombre}': ", minimo=0.0)
        cart[nombre] = (cantidad, precio)
        print(f"→ Añadido: {nombre} = ({cantidad}, {precio})\n")
    return cart


def elegir_carrito() -> Dict[str, Tuple[int, float]]:
    print("\n=== Selección de carrito ===")
    print("1) Carrito ejemplo simple (huevos)")
    print("2) Carrito ejemplo múltiple")
    print("3) Crear carrito manualmente")
    op = leer_opcion("Elige opción (1/2/3): ", {"1", "2", "3"})
    if op == "1":
        return {"huevos": (2, 0.55)}  # total 1.10
    elif op == "2":
        return {
            "camiseta": (2, 19.99),
            "pantalon": (1, 39.99),
            "calcetines": (3, 2.50),
        }
    else:
        return crear_carrito_manual()


# -----------------------------------------
# Submenú para editar carrito
# -----------------------------------------
def editar_añadir(cart):
    nombre = input("Nombre del producto: ").strip()
    if nombre == "":
        print("Nombre vacío, cancelado.\n")
        return
    cantidad = prompt_int("Cantidad: ", minimo=1)
    precio = prompt_float("Precio unitario: ", minimo=0.0)
    cart[nombre] = (cantidad, precio)
    print(f"→ Añadido {nombre}: ({cantidad}, {precio})\n")


def editar_eliminar(cart):
    nombre = input("Producto a eliminar: ").strip()
    if nombre not in cart:
        print("Ese producto no está en el carrito.\n")
        return
    del cart[nombre]
    print(f"→ Eliminado {nombre}\n")


def editar_modificar(cart):
    nombre = input("Producto a modificar: ").strip()
    if nombre not in cart:
        print("Ese producto no existe.\n")
        return

    cantidad = prompt_int("Nueva cantidad: ", minimo=1)
    precio = prompt_float("Nuevo precio unitario: ", minimo=0.0)
    cart[nombre] = (cantidad, precio)
    print(f"→ Actualizado {nombre}: ({cantidad}, {precio})\n")


def submenu_editar_carrito(cart):
    while True:
        print("\n=== Editar carrito ===")
        print("1) Añadir producto")
        print("2) Eliminar producto")
        print("3) Modificar producto")
        print("4) Ver carrito")
        print("5) Terminar edición")
        
        op = leer_opcion("Selecciona (1/2/3/4/5): ", {"1","2","3","4","5"})
        
        if op == "1":
            editar_añadir(cart)
        elif op == "2":
            editar_eliminar(cart)
        elif op == "3":
            editar_modificar(cart)
        elif op == "4":
            try:
                imprimir_carrito(cart)
            except Exception as e:
                print(f"(Carrito no válido aún): {e}\n")
        else:
            print("Edición terminada.\n")
            break


# -----------------------------------------
# Menú de métodos de pago
# -----------------------------------------
def elegir_metodo_pago_interactivo():
    print("\n=== Método de pago ===")
    print("1) Bizum")
    print("2) Tarjeta de crédito")
    print("3) PayPal")
    print("4) Al contado (pendiente)")
    while True:
        op = leer_opcion("Elige opción (1/2/3/4): ", {"1", "2", "3", "4"})
        try:
            if op == "1":
                phone = prompt_no_vacio("Teléfono (+34...): ")
                metodo = BizumPayment(phone=phone)
                return metodo, "BIZUM"
            elif op == "2":
                number = prompt_no_vacio("Número de tarjeta (solo dígitos o con espacios): ")
                expiry = prompt_no_vacio("Caducidad (MM/YY): ")
                cvv = prompt_no_vacio("CVV (3-4 dígitos): ")
                holder = input("Titular (opcional): ").strip() or None
                metodo = CreditCardPayment(number=number, expiry_mm_yy=expiry, cvv=cvv, holder_name=holder)
                return metodo, "TARJETA"
            elif op == "3":
                email = prompt_no_vacio("Email de PayPal: ")
                password = prompt_no_vacio("Contraseña de PayPal: ")
                metodo = PayPalPayment(email=email, password=password)
                return metodo, "PAYPAL"
            else:
                return CashPayment(), "CONTADO"
        except ValueError as e:
            print(f"⚠️ Datos inválidos: {e}. Vuelve a intentarlo.\n")


# -----------------------------------------
# Bucle principal
# -----------------------------------------
def main():
    print("=====================================")
    print("   DEMO PASARELA DE PAGOS (con menú) ")
    print("=====================================")
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1) Procesar un pago")
        print("2) Ver historial de pagos")
        print("3) Salir")
        op = leer_opcion("Elige (1/2/3): ", {"1","2","3"})

        if op == "1":
            try:
                carrito = elegir_carrito()
                submenu_editar_carrito(carrito)
                # Validamos antes de continuar (no permitir carrito vacío)
                validar_carrito(carrito)

                metodo, nombre = elegir_metodo_pago_interactivo()
                resultado = procesar_pago(carrito, metodo, currency="EUR")
                comprobar_resultado(carrito, nombre, resultado)
                registrar_pago(carrito, nombre, resultado)

            except Exception as e:
                print(f"💥 Se produjo un error durante el procesamiento: {e}\n")

        elif op == "2":
            ver_historial()

        else:
            print("¡Hasta la próxima!")
            break


if __name__ == "__main__":
    main()