from datetime import datetime, timedelta
from app.db.database import Database
from app.models.dtos import AlertaCuotaDTO, EstadoCreditoDTO
from app.services.notification_templates import NotificationTemplates


class NotificationService:
    def __init__(self):
        self.db = Database()

    def generar_plan_cuotas(self, venta_id: int, cuotas_totales: int, monto_cuota: float, cursor) -> None:
        """
        Genera el cronograma de pagos quincenales.
        Debe llamarse dentro de una transacción activa (usando el cursor provisto).
        """
        if cuotas_totales <= 0:
            return

        fecha_actual = datetime.now()

        for i in range(1, cuotas_totales + 1):
            # Cada 14 días (Quincenal)
            dias_sumar = i * 14
            fecha_venc = (fecha_actual + timedelta(days=dias_sumar)).strftime("%Y-%m-%d")

            cursor.execute(
                """
                INSERT INTO cuotas (venta_id, numero_cuota, fecha_vencimiento, monto_usd, estado)
                VALUES (?, ?, ?, ?, ?)
            """,
                (venta_id, i, fecha_venc, monto_cuota, "Pendiente"),
            )

    def obtener_alertas_proximas(self, dias_anticipacion=1) -> list[AlertaCuotaDTO]:
        """
        [DEPRECATED/LEGACY] Mantiene compatibilidad si algo más lo usa.
        Busca cuotas que vencen pronto (Standard).
        """
        return self._query_alerts_by_date_range(days_ahead=dias_anticipacion)

    def get_urgent_badge_count(self) -> int:
        """
        Regla 1: Badge de la Campanita (ALERTA)
        Refleja ÚNICAMENTE cuotas que vencen HOY o MAÑANA (24h ventana).
        """
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*)
            FROM cuotas q
            JOIN ventas v ON q.venta_id = v.id
            WHERE q.fecha_vencimiento IN (?, ?)
            AND q.estado = 'Pendiente'
            AND v.saldo_pendiente_usd > 0
        """

        cursor.execute(query, (today, tomorrow))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_all_credits_status(self) -> list[EstadoCreditoDTO]:
        """
        Regla 2: Ventana de Notificaciones (CONTROL TOTAL)
        Retorna TODOS los créditos activos con su estado calculado.
        Estados:
          - 🔴 Vencido: Cuota pendiente con fecha < Hoy
          - 🟠 Próximo: Cuota pendiente con fecha entre Hoy y Hoy+3 días
          - 🟢 Al día: El resto
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Obtenemos ventas activas y su cuota pendiente MÁS ANTIGUA (o próxima)
        # Esto asume que si debes la cuota 1 y 2, la urgencia la dicta la 1.
        query = """
            SELECT 
                v.id, 
                c.nombre, 
                i.nombre, 
                MIN(q.fecha_vencimiento) as proxima_fecha,
                q.monto_usd,
                v.saldo_pendiente_usd,
                q.numero_cuota
            FROM ventas v
            JOIN clientes c ON v.id_cliente = c.id
            JOIN inventario i ON v.id_telefono = i.id
            JOIN cuotas q ON v.id = q.venta_id
            WHERE v.saldo_pendiente_usd > 0 
            AND q.estado = 'Pendiente'
            GROUP BY v.id
            ORDER BY proxima_fecha ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        resultados = []
        today_date = datetime.now().date()

        for row in rows:
            venta_id, cliente, producto, fecha_venc_str, monto_cuota, saldo, num_cuota = row

            fecha_venc = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
            delta_days = (fecha_venc - today_date).days

            # Clasificación de Estado
            estado_label = "🟢 Al día"
            dias_mora = 0

            if delta_days < 0:
                estado_label = "🔴 Vencido"
                dias_mora = abs(delta_days)
            elif 0 <= delta_days <= 3:
                estado_label = "🟠 Próximo"

            # Generar mensaje sugerido
            mensaje = NotificationTemplates.render_recordatorio(
                cliente_nombre=cliente,
                producto_nombre=producto,
                num_cuota=num_cuota,
                monto_usd=monto_cuota,
                fecha_vence=fecha_venc_str,
            )

            resultados.append(
                EstadoCreditoDTO(
                    venta_id=venta_id,
                    cliente_nombre=cliente,
                    producto_nombre=producto,
                    estado_etiqueta=estado_label,
                    saldo_pendiente_usd=saldo,
                    proxima_cuota_fecha=fecha_venc_str,
                    proxima_cuota_monto=monto_cuota,
                    dias_mora=dias_mora,
                    mensaje_sugerido=mensaje,
                )
            )

        return resultados

    def _query_alerts_by_date_range(self, days_ahead: int) -> list[AlertaCuotaDTO]:
        target_dates = []
        for i in range(days_ahead + 1):
            d = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            target_dates.append(d)

        placeholders = ",".join(["?"] * len(target_dates))

        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = f"""
            SELECT c.nombre, i.nombre, q.numero_cuota, q.monto_usd, q.fecha_vencimiento, v.saldo_pendiente_usd
            FROM cuotas q
            JOIN ventas v ON q.venta_id = v.id
            JOIN clientes c ON v.id_cliente = c.id
            JOIN inventario i ON v.id_telefono = i.id
            WHERE q.fecha_vencimiento IN ({placeholders})
            AND q.estado = 'Pendiente'
            AND v.saldo_pendiente_usd > 0
        """

        cursor.execute(query, target_dates)
        rows = cursor.fetchall()
        conn.close()

        alertas = []
        for row in rows:
            mensaje = NotificationTemplates.render_recordatorio(
                cliente_nombre=row[0], producto_nombre=row[1], num_cuota=row[2], monto_usd=row[3], fecha_vence=row[4]
            )
            alertas.append(
                AlertaCuotaDTO(
                    cliente_nombre=row[0],
                    producto_nombre=row[1],
                    num_cuota=row[2],
                    monto_cuota=row[3],
                    fecha_vencimiento=row[4],
                    saldo_venta_actual=row[5],
                    mensaje_cliente=mensaje,
                )
            )
        return alertas
