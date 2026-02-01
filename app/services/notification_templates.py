class NotificationTemplates:
    """
    Gestor centralizado de plantillas de mensajes.
    Garantiza que toda comunicación sea humana, consistente y profesional.
    """

    # Plantillas Base
    CUOTA_RECORDATORIO = """Hola {cliente} 👋

Te recordamos que mañana {fecha_vencimiento} corresponde el pago de tu cuota #{num_cuota} ({producto}) por un monto de ${monto_usd} USD.

Evita recargos realizando tu pago a tiempo.
Cualquier duda, estamos a la orden.
Gracias por tu confianza 🙌"""

    CUOTA_VENCIDA = """Hola {cliente} ⚠️

Notamos que tu cuota #{num_cuota} ({producto}) venció el {fecha_vencimiento}.
Saldo pendiente: ${monto_usd} USD.

Por favor reporta tu pago lo antes posible para mantener tu crédito activo.
Saludos."""

    @staticmethod
    def render_recordatorio(cliente_nombre, producto_nombre, num_cuota, monto_usd, fecha_vence):
        """Genera el mensaje de recordatorio estándar."""
        return NotificationTemplates.CUOTA_RECORDATORIO.format(
            cliente=cliente_nombre,
            producto=producto_nombre,
            num_cuota=num_cuota,
            monto_usd=f"{monto_usd:.2f}",
            fecha_vencimiento=fecha_vence,
        )

    @staticmethod
    def render_vencimiento(cliente_nombre, producto_nombre, num_cuota, monto_usd, fecha_vence):
        """Genera el mensaje de cobro para cuotas vencidas."""
        return NotificationTemplates.CUOTA_VENCIDA.format(
            cliente=cliente_nombre,
            producto=producto_nombre,
            num_cuota=num_cuota,
            monto_usd=f"{monto_usd:.2f}",
            fecha_vencimiento=fecha_vence,
        )
