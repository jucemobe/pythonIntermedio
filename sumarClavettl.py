import time
import inspect
import functools
import threading
from typing import Optional, Any, Dict

def ttl(seconds: float, *, expired_value: Optional[Any] = None):
    """
    Decorador con TTL para argumentos de contraseña.
    - seconds: segundos que la contraseña permanece disponible.
    - expired_value: valor que se inyectará como 'password' al expirar (por defecto None).
    
    Comportamiento:
    • La primera vez que se llama con 'password' no None, se guarda y arranca el TTL.
    • Llamadas posteriores dentro del TTL reutilizan la contraseña guardada (aunque no se pase).
    • Al expirar, la contraseña se descarta y 'password' se fuerza a expired_value (p.ej. None).
    • Si tras expirar vuelves a pasar una contraseña explícita, se reinicia el TTL.
    """
    if seconds is None or seconds <= 0:
        raise ValueError("seconds debe ser un número positivo.")

    def decorator(func):
        sig = inspect.signature(func)
        if "password" not in sig.parameters:
            raise TypeError(f"La función '{func.__name__}' debe tener un argumento llamado 'password'.")

        # Estado por función decorada
        lock = threading.Lock()
        state: Dict[str, Any] = {
            "stored_password": None,   # última contraseña válida
            "expires_at": 0.0,         # epoch de expiración
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal state

            # Enlazar args/kwargs para operar uniformemente sobre 'password'
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            now = time.time()
            with lock:
                # ¿Ha expirado lo guardado?
                if state["stored_password"] is not None and now >= state["expires_at"]:
                    # Expiró → borrar
                    state["stored_password"] = None
                    state["expires_at"] = 0.0

                passed_password = bound.arguments.get("password", None)

                if passed_password is not None:
                    # El usuario ha proporcionado una contraseña explícita → guardar y renovar TTL
                    state["stored_password"] = passed_password
                    state["expires_at"] = now + seconds
                else:
                    # No se pasó password explícita
                    if state["stored_password"] is not None:
                        # Hay password viva → inyectar
                        bound.arguments["password"] = state["stored_password"]
                    else:
                        # No hay password viva → forzar valor expirado
                        bound.arguments["password"] = expired_value

            # Llamar a la función con los argumentos ajustados
            return func(*bound.args, **bound.kwargs)

        # utilidades opcionales
        def ttl_info():
            with lock:
                remaining = max(0.0, state["expires_at"] - time.time()) if state["stored_password"] is not None else 0.0
                return {
                    "has_password": state["stored_password"] is not None,
                    "expires_at": state["expires_at"],
                    "seconds_remaining": round(remaining, 3),
                    "ttl_seconds": seconds,
                }

        def ttl_clear():
            with lock:
                state["stored_password"] = None
                state["expires_at"] = 0.0

        wrapper.ttl_info = ttl_info
        wrapper.ttl_clear = ttl_clear
        return wrapper

    return decorator

# =========================
# Ejemplo de uso solicitado
# =========================
@ttl(30)  # 30 segundos de vida para la contraseña
def sumar_con_contraseña(n1, n2, password="admin"):
    # Para ver qué está recibiendo la función:
    print(f"password = {password!r}")
    return n1 + n2

if __name__ == "__main__":
    print("-- Primera llamada: paso 'password' explícita → arranca TTL --")
    print("resultado:", sumar_con_contraseña(2, 3, password="secreta"))  # imprime 'secreta'

    print("\n-- Segunda llamada: NO paso password, pero el TTL sigue vivo → se inyecta la guardada --")
    print("resultado:", sumar_con_contraseña(4, 5))  # imprime 'secreta'

    print("\nEsperando a que expire (31s)...")
    time.sleep(31)

    print("\n-- Tercera llamada: TTL expirado → password se elimina y se fuerza a None (o expired_value) --")
    print("resultado:", sumar_con_contraseña(6, 7))  # imprime None

    print("\nInfo TTL:", sumar_con_contraseña.ttl_info())