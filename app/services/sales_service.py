from datetime import datetime
from app.db.database import Database

# from app.models.venta import Venta
from app.services.inventory_service import ServiceInventario
from app.services.notification_service import NotificationService
from app.models.dtos import CalculoVentaDTO
from app.utils.exceptions import BusinessRuleError
from app.utils.enums import EstadoVenta, TipoVenta


class ServiceVentas:
    """
    Servicio para gestionar operaciones de ventas.

    Maneja cálculos de precios, procesamiento de ventas, y actualizaciones de stock.
    """

    def __init__(self):
        self.db = Database()
        self.servicio_inventario = ServiceInventario()
        self.servicio_notificacion = NotificationService()

    def calcular_precio_con_margen(self, costo_original, margen_porcentaje):
        """
        Calcula el precio final basado en el costo y el margen.
        Centraliza esta lógica para asegurar consistencia.
        """
        if costo_original < 0:
            costo_original = 0
        if margen_porcentaje < 0:
            margen_porcentaje = 0
        return costo_original * (1 + margen_porcentaje / 100)

    def calcular_totales_venta(self, precio_final_usd, pago_inicial_usd, cuotas_totales, tasa_cambio):
        """
        Realiza todos los cálculos financieros de una venta.
        Retorna un diccionario con los resultados.
        """
        # Validaciones básicas
        if pago_inicial_usd < 0:
            pago_inicial_usd = 0

        if pago_inicial_usd > precio_final_usd:
            # Validación de regla de negocio
            raise BusinessRuleError("El pago inicial no puede ser mayor al precio final.")

        # Lógica de Contado vs Crédito
        es_contado = cuotas_totales == 0

        if es_contado:
            saldo_pendiente_usd = 0.0
            monto_cuota_usd = 0.0
            estado = EstadoVenta.PAGADA
            # En contado, se asume que se paga todo, aunque el input diga 0
            # Pero la UI debe mandar el pago completo si es contado.
            # Si el pago inicial es menor, es deuda. Pero si cuotas es 0, es contradicción.
            # Asumimos que CONTADO significa pago_inicial == precio_final
            pago_inicial_usd = precio_final_usd
        else:
            saldo_pendiente_usd = precio_final_usd - pago_inicial_usd
            if saldo_pendiente_usd < 0:
                saldo_pendiente_usd = 0

            monto_cuota_usd = saldo_pendiente_usd / cuotas_totales if cuotas_totales > 0 else 0
            estado = EstadoVenta.ACTIVA

        # Cálculos en Bs
        precio_final_bs = precio_final_usd * tasa_cambio
        monto_cuota_bs = monto_cuota_usd * tasa_cambio

        return CalculoVentaDTO(
            precio_final_usd=precio_final_usd,
            pago_inicial_usd=pago_inicial_usd,
            saldo_pendiente_usd=saldo_pendiente_usd,
            cuotas_totales=cuotas_totales,
            monto_cuota_usd=monto_cuota_usd,
            estado=estado,
            es_contado=es_contado,
            precio_final_bs=precio_final_bs,
            monto_cuota_bs=monto_cuota_bs,
        )

    def procesar_venta(self, id_cliente, id_telefono, precio_final_usd, pago_inicial_usd, cuotas_totales, tasa_cambio):

        # 1. Realizar cálculos finales (Source of Truth)
        calculos = self.calcular_totales_venta(precio_final_usd, pago_inicial_usd, cuotas_totales, tasa_cambio)

        tipo_venta = TipoVenta.CONTADO if calculos.es_contado else TipoVenta.FINANCIADO
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # 2. Actualizar Stock (Atomicidad: Pasamos el cursor)
            # Restamos 1 al stock
            self.servicio_inventario.actualizar_stock(id_telefono, -1, cursor=cursor)

            # 3. Registrar Venta
            cursor.execute(
                """
                INSERT INTO ventas (
                    id_cliente, id_telefono, fecha, tipo_venta, precio_final_usd,
                    pago_inicial_usd, saldo_pendiente_usd, cuotas_totales,
                    monto_cuota_usd, tasa_cambio_usada, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    id_cliente,
                    id_telefono,
                    fecha,
                    tipo_venta,
                    calculos.precio_final_usd,
                    calculos.pago_inicial_usd,
                    calculos.saldo_pendiente_usd,
                    calculos.cuotas_totales,
                    calculos.monto_cuota_usd,
                    tasa_cambio,
                    calculos.estado,
                ),
            )

            # 4. Generar Plan de Cuotas (Si aplica)
            if not calculos.es_contado:
                # Obtenemos el ID de la venta recién creada
                venta_id = cursor.lastrowid
                self.servicio_notificacion.generar_plan_cuotas(
                    venta_id, calculos.cuotas_totales, calculos.monto_cuota_usd, cursor
                )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def obtener_historial_ventas(self, customer_id=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT v.id, v.fecha, c.nombre, t.nombre, v.tipo_venta, v.precio_final_usd, v.saldo_pendiente_usd
            FROM ventas v
            JOIN clientes c ON v.id_cliente = c.id
            JOIN inventario t ON v.id_telefono = t.id
        """

        params = ()
        if customer_id:
            query += " WHERE v.id_cliente = ?"
            params = (customer_id,)

        query += " ORDER BY v.fecha DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
