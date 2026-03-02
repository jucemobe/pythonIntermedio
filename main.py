# main.py
# Ejemplos de uso del sistema de notificaciones + servicio de alertas.
# Asegúrate de tener el archivo 'notificaciones.py' en la misma carpeta
# con las clases: Notificacion, Notificador, SmsNotificador, EmailNotificador,
# PushNotificador, NotificadorFactory, ServicioAlertas

from notificaciones import (
    Notificacion,
    SmsNotificador,
    EmailNotificador,
    PushNotificador,
    NotificadorFactory,
    ServicioAlertas,
)


def separador(titulo: str) -> None:
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)


def demo_inyeccion_sms() -> None:
    separador("1) Inyección directa: SMS")
    servicio = ServicioAlertas(notificador=SmsNotificador(proveedor="Twilio", remitente="MiApp"))
    servicio.alertar(Notificacion(destino="+34123456789", mensaje="Tu código es 123456"))


def demo_inyeccion_email() -> None:
    separador("2) Cambiar a Email por inyección")
    servicio = ServicioAlertas()
    servicio.configurar_notificador(
        EmailNotificador(smtp_host="smtp.miempresa.com", remitente="alertas@miempresa.com")
    )
    servicio.alertar(
        Notificacion(
            destino="usuario@correo.com",
            asunto="Aviso de seguridad",
            mensaje="Se detectó un acceso inusual a tu cuenta.",
        )
    )


def demo_factory_push() -> None:
    separador("3) Uso de fábrica: Push")
    servicio = ServicioAlertas()
    servicio.alertar_con_tipo(
        "push",
        Notificacion(destino="DEVICE_TOKEN_ABC", asunto="Recordatorio", mensaje="Tienes una tarea pendiente."),
        proveedor="FCM",
        app_id="producto-app",
    )


def demo_registro_custom_webhook() -> None:
    separador("4) Registrar un canal custom en la fábrica y usarlo (Webhook)")

    # Definimos un notificador personalizado (p. ej., Webhook) sin tocar el servicio ni la fábrica:
    from notificaciones import Notificador  # usamos la interfaz para heredar

    class WebhookNotificador(Notificador):
        def __init__(self, url: str):
            self.url = url

        def enviar(self, notif: Notificacion) -> None:
            # Integración real: POST JSON a self.url
            print(
                f"[WEBHOOK] POST {self.url} -> "
                f"{{destino: {notif.destino}, asunto: {notif.asunto}, mensaje: {notif.mensaje}}}"
            )

    # Lo registramos dinámicamente en la fábrica:
    NotificadorFactory.registrar("webhook", WebhookNotificador)

    # Y lo usamos a partir del tipo:
    servicio = ServicioAlertas()
    servicio.alertar_con_tipo(
        "webhook",
        Notificacion(destino="canal-interno", asunto="Build OK", mensaje="CI/CD finalizado."),
        url="https://hooks.internal/alerts",
    )


def demo_errores_validacion() -> None:
    separador("5) Manejo básico de errores (validaciones por canal)")
    servicio = ServicioAlertas(notificador=SmsNotificador(proveedor="Twilio"))
    try:
        # Falta el destino en SMS → debe lanzar ValueError
        servicio.alertar(Notificacion(destino="", mensaje="Mensaje sin número"))
    except ValueError as e:
        print(f"[OK] Capturado ValueError esperado: {e}")

    # Email sin asunto es válido (usa '(sin asunto)')
    servicio.configurar_notificador(EmailNotificador())
    servicio.alertar(Notificacion(destino="persona@ejemplo.com", mensaje="Email sin asunto"))


def demo_cambio_dinamico_de_canal() -> None:
    separador("6) Cambio dinámico de canal en tiempo de ejecución")
    servicio = ServicioAlertas(SmsNotificador())
    servicio.alertar(Notificacion(destino="+34000000000", mensaje="Enviado por SMS"))

    # Cambiamos a Push sin reconstruir el servicio
    servicio.configurar_notificador(PushNotificador(proveedor="MockPush", app_id="demo"))
    servicio.alertar(Notificacion(destino="TOKEN_XYZ", asunto="Hola", mensaje="Ahora por Push"))


def main() -> None:
    demo_inyeccion_sms()
    demo_inyeccion_email()
    demo_factory_push()
    demo_registro_custom_webhook()
    demo_errores_validacion()
    demo_cambio_dinamico_de_canal()


if __name__ == "__main__":
    main()