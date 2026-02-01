class Venta:
    def __init__(
        self,
        id,
        id_cliente,
        id_telefono,
        fecha,
        tipo_venta,
        precio_final_usd,
        pago_inicial_usd,
        saldo_pendiente_usd,
        cuotas_totales,
        monto_cuota_usd,
        tasa_cambio_usada,
        estado,
    ):
        self.id = id
        self.id_cliente = id_cliente
        self.id_telefono = id_telefono
        self.fecha = fecha
        self.tipo_venta = tipo_venta
        self.precio_final_usd = precio_final_usd
        self.pago_inicial_usd = pago_inicial_usd
        self.saldo_pendiente_usd = saldo_pendiente_usd
        self.cuotas_totales = cuotas_totales
        self.monto_cuota_usd = monto_cuota_usd
        self.tasa_cambio_usada = tasa_cambio_usada
        self.estado = estado

    @staticmethod
    def from_row(row):
        return Venta(*row)
