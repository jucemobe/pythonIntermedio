# --- NUEVO Notificador JSON ---
import json
import sys

from abc import ABC, abstractmethod


# =========================
# Modelo (definición común)
# =========================
class Notificacion:
    """Definición de la notificación independiente del canal."""
    def __init__(self, destino: str, asunto=None, mensaje: str = "", metadatos=None):
        # destino: teléfono, email, device token, etc.
        self.destino = destino
        self.asunto = asunto  # puede ser None
        self.mensaje = mensaje
        self.metadatos = metadatos if metadatos is not None else {}  # dict simple

    def __repr__(self) -> str:
        return (f"Notificacion(destino={self.destino!r}, asunto={self.asunto!r}, "
                f"mensaje={self.mensaje!r}, metadatos={self.metadatos!r})")


# =========================
# Interfaz (puerto)
# =========================
class Notificador(ABC):
    """Interfaz del notificador (contrato común para todos los canales)."""
    @abstractmethod
    def enviar(self, notif: Notificacion) -> None:
        """Envía la notificación por el canal concreto."""
        ...


# ==========================================
# Implementaciones concretas (adaptadores)
# ==========================================
class SmsNotificador(Notificador):
    def __init__(self, proveedor: str = "MockSMS", remitente: str = None):
        self.proveedor = proveedor
        self.remitente = remitente or "App"

    def enviar(self, notif: Notificacion) -> None:
        # Aquí iría la integración real con un gateway SMS (Twilio, etc.)
        if not notif.destino:
            raise ValueError("Para SMS, 'destino' debe ser un número de teléfono.")
        print(f"[SMS/{self.proveedor}] De: {self.remitente} → A: {notif.destino} :: {notif.mensaje}")


class EmailNotificador(Notificador):
    def __init__(self, smtp_host: str = "smtp.example.com", remitente: str = "noreply@example.com"):
        self.smtp_host = smtp_host
        self.remitente = remitente

    def enviar(self, notif: Notificacion) -> None:
        # Aquí iría la integración real con SMTP o proveedor (SES, SendGrid, etc.)
        if not notif.destino:
            raise ValueError("Para Email, 'destino' debe ser una dirección de correo.")
        asunto = notif.asunto or "(sin asunto)"
        print(f"[EMAIL/{self.smtp_host}] From: {self.remitente} → To: {notif.destino} :: {asunto}\n{notif.mensaje}")


class PushNotificador(Notificador):
    def __init__(self, proveedor: str = "MockPush", app_id: str = None):
        self.proveedor = proveedor
        self.app_id = app_id or "demo-app"

    def enviar(self, notif: Notificacion) -> None:
        # Aquí iría la integración real con FCM/APNS/OneSignal/etc.
        if not notif.destino:
            raise ValueError("Para Push, 'destino' debe ser un device token / canal válido.")
        title = notif.asunto or "Notificación"
        print(f"[PUSH/{self.proveedor}] App: {self.app_id} → Token: {notif.destino} :: {title} — {notif.mensaje}")

class JsonNotificador(Notificador):
    """
    Emite la notificación en formato JSON.
    - pretty: si True, salida indentada; si False, compacta en una línea.
    - stream: 'stdout' (por defecto) o 'stderr'. Ignorado si file_path está definido.
    - file_path: si se indica, vuelca el JSON línea a línea en el archivo (modo append).
    - extra: dict opcional para añadir campos adicionales (app, env, trace_id, etc.).
    """
    def __init__(self, pretty=False, stream="stdout", file_path=None, extra=None):
        self.pretty = bool(pretty)
        self.stream = stream
        self.file_path = file_path
        self.extra = extra if isinstance(extra, dict) else {}

    def enviar(self, notif: Notificacion) -> None:
        payload = {
            "canal": "json",
            "destino": notif.destino,
            "asunto": notif.asunto,
            "mensaje": notif.mensaje,
            "metadatos": notif.metadatos,
        }
        # Merge "extra" sin sobreescribir claves principales
        for k, v in self.extra.items():
            if k not in payload:
                payload[k] = v

        data = (
            json.dumps(payload, ensure_ascii=False, indent=2)
            if self.pretty
            else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        )

        # Prioridad archivo si se especifica
        if self.file_path:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(data + "\n")
            return

        # Si no hay archivo, dirigir a stream
        if self.stream == "stderr":
            print(data, file=sys.stderr)
        else:
            print(data)  # stdout
            
# ==========================================
# Fábrica (opcional, para crear notificador)
# ==========================================
class NotificadorFactory:
    _registry = {
        "sms": SmsNotificador,
        "email": EmailNotificador,
        "push": PushNotificador,
#        "webhook": WebhookNotificador,  # si lo usas
        "json": JsonNotificador,        # ← AÑADIR ESTA LÍNEA
    }

    @classmethod
    def registrar(cls, tipo: str, clase_notificador) -> None:
        cls._registry[tipo.lower()] = clase_notificador

    @classmethod
    def crear(cls, tipo: str, **kwargs) -> Notificador:
        key = tipo.lower()
        if key not in cls._registry:
            soportados = list(cls._registry.keys())
            raise ValueError(f"Tipo de notificador no soportado: {tipo}. Soportados: {soportados}")
        # ← CORRECTO: instanciamos la clase registrada
        return cls._registry[key](**kwargs)
    
# ==========================================
# Servicio de Alertas (usa inyección)
# ==========================================
class ServicioAlertas:
    """Orquesta el envío utilizando un Notificador inyectado o una fábrica."""
    def __init__(self, notificador: Notificador = None):
        self._notificador = notificador

    def configurar_notificador(self, notificador: Notificador) -> None:
        self._notificador = notificador

    def alertar(self, notif: Notificacion) -> None:
        if self._notificador is None:
            raise RuntimeError("No hay notificador configurado en el Servicio de Alertas.")
        # Lógica transversal (validaciones, plantillas, auditoría, reintentos, etc.) podría ir aquí
        self._notificador.enviar(notif)

    # Conveniencia: usar fábrica directamente
    def alertar_con_tipo(self, tipo: str, notif: Notificacion, **kwargs) -> None:
        notificador = NotificadorFactory.crear(tipo, **kwargs)
        notificador.enviar(notif)
