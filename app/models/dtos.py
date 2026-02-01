"""
Objetos de Transferencia de Datos (DTOs).
Estructuras inmutables para pasar datos entre capas con tipado fuerte.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculoVentaDTO:
    """
    Resultado de los cálculos financieros de una venta.
    Contiene valores en USD y sus conversiones a Bs.
    """

    # Valores Base (USD)
    precio_final_usd: float
    pago_inicial_usd: float
    saldo_pendiente_usd: float

    # Configuración Venta
    cuotas_totales: int
    monto_cuota_usd: float
    es_contado: bool
    estado: str  # "Pagada" | "Activa"

    # Valores Convertidos (Bs)
    precio_final_bs: float
    monto_cuota_bs: float


@dataclass(frozen=True)
class ResumenVentaDTO:
    """Para mostrar ventas en listados o reportes"""

    id: int
    fecha: str
    cliente: str
    producto: str
    tipo: str
    total_usd: float
    saldo_usd: float


@dataclass(frozen=True)
class AbonoDTO:
    """Representa un pago parcial registrado."""

    venta_id: int
    fecha: str
    monto_usd: float
    monto_bs: float
    tasa_cambio: float
    notas: str = ""
    metodo: str = "Efectivo"


@dataclass(frozen=True)
class AlertaCuotaDTO:
    """Datos para notificar una cuota próxima a vencer (Legacy/Simple)."""

    cliente_nombre: str
    producto_nombre: str
    num_cuota: int
    monto_cuota: float
    fecha_vencimiento: str
    saldo_venta_actual: float
    mensaje_cliente: str = ""


@dataclass(frozen=True)
class EstadoCreditoDTO:
    """
    Representa el estado completo de un crédito para el panel de control.
    """

    venta_id: int
    cliente_nombre: str
    producto_nombre: str
    # Estado calculado: "Al día", "Próximo (3 días)", "Vencido"
    estado_etiqueta: str
    # Datos deuda
    saldo_pendiente_usd: float
    proxima_cuota_fecha: str
    proxima_cuota_monto: float
    dias_mora: int = 0
    mensaje_sugerido: str = ""
