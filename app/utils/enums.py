from enum import Enum


class EstadoVenta(str, Enum):
    ACTIVA = "Activa"
    PAGADA = "Pagada"
    PENDIENTE = "Pendiente"


class TipoVenta(str, Enum):
    CONTADO = "Contado"
    FINANCIADO = "Financiado"
