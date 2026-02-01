"""
Excepciones personalizadas para el dominio de SmartCredit.
Permite manejar errores de negocio de forma semántica.
"""


class SmartCreditError(Exception):
    """Clase base para todas las excepciones controladas de la app."""

    def __init__(self, mensaje, codigo=None):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)


class BusinessRuleError(SmartCreditError):
    """
    Se levanta cuando se viola una regla de negocio.
    Ej: Pago inicial mayor al precio total.
    """


class InventoryError(SmartCreditError):
    """
    Se levanta cuando hay problemas con el inventario.
    Ej: Stock insuficiente.
    """


class DatabaseConnectionError(SmartCreditError):
    """Error crítico de conexión a datos."""
