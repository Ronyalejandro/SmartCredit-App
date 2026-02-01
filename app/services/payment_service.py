from datetime import datetime
from app.db.database import Database
from app.models.dtos import AbonoDTO
from app.utils.exceptions import BusinessRuleError


class PaymentService:
    def __init__(self):
        self.db = Database()
        self._ensure_schema()

    def _ensure_schema(self):
        """Valida que la tabla abonos tenga las columnas necesarias (migración suave)."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(abonos)")
            columns = [info[1] for info in cursor.fetchall()]
            if "metodo" not in columns:
                cursor.execute("ALTER TABLE abonos ADD COLUMN metodo TEXT DEFAULT 'Efectivo'")
                conn.commit()
        finally:
            conn.close()

    def registrar_abono(
        self, venta_id: int, monto_usd: float, tasa_cambio: float, metodo: str = "Efectivo", notas: str = ""
    ) -> bool:
        """
        # Región: Gestión de Abonos
        Registra un abono, actualiza el saldo de la venta y marca cuotas como pagadas.
        Transaccional y atómico.
        """
        if monto_usd <= 0:
            raise BusinessRuleError("El monto del abono debe ser mayor a 0.")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Verificar Estado Actual de la Venta
            cursor.execute("SELECT saldo_pendiente_usd, estado FROM ventas WHERE id = ?", (venta_id,))
            row = cursor.fetchone()
            if not row:
                raise BusinessRuleError("Venta no encontrada.")

            saldo_actual, estado_venta = row

            if estado_venta == "Pagada" or saldo_actual <= 0:
                raise BusinessRuleError("La venta ya está pagada por completo.")

            if monto_usd > saldo_actual:
                raise BusinessRuleError(f"El abono (${monto_usd}) excede el saldo pendiente (${saldo_actual}).")

            # 2. Registrar Abono
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            monto_bs = monto_usd * tasa_cambio

            cursor.execute(
                """
                INSERT INTO abonos (venta_id, fecha, monto_usd, tasa_cambio, monto_bs, notas, metodo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (venta_id, fecha, monto_usd, tasa_cambio, monto_bs, notas, metodo),
            )

            # 3. Actualizar Saldo Venta
            nuevo_saldo = saldo_actual - monto_usd
            # Fix flotante
            if nuevo_saldo < 0.01:
                nuevo_saldo = 0

            nuevo_estado = "Pagada" if nuevo_saldo == 0 else "Activa"

            cursor.execute(
                """
                UPDATE ventas 
                SET saldo_pendiente_usd = ?, estado = ?
                WHERE id = ?
            """,
                (nuevo_saldo, nuevo_estado, venta_id),
            )

            # 4. Conciliar Cuotas (Lógica Simplificada)
            # Marcar cuotas como pagadas en orden de antigüedad hasta cubrir el monto abonado
            # NOTA: Esta lógica asume que el abono se imputa a la cuota más antigua.
            # Si el abono es parcial sobre una cuota, la cuota sigue "Pendiente" o podríamos manejar "Parcial".
            # Por simplicidad y robustez: Si Saldo Venta == 0, todas las cuotas se marcan pagadas.
            if nuevo_estado == "Pagada":
                cursor.execute("UPDATE cuotas SET estado = 'Pagada' WHERE venta_id = ?", (venta_id,))
            else:
                # Opcional: Podríamos marcar cuotas individuales si el usuario pagó el exacto.
                # Para evitar complejidad, dejaremos las cuotas sincronizadas con el saldo global
                # en futuras iteraciones.
                pass

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def obtener_abonos_por_venta(self, venta_id: int) -> list[AbonoDTO]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT venta_id, fecha, monto_usd, monto_bs, tasa_cambio, notas, metodo
            FROM abonos
            WHERE venta_id = ?
            ORDER BY fecha DESC
        """,
            (venta_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        abonos = []
        for row in rows:
            abonos.append(
                AbonoDTO(
                    venta_id=row[0],
                    fecha=row[1],
                    monto_usd=row[2],
                    monto_bs=row[3],
                    tasa_cambio=row[4],
                    notas=row[5],
                    metodo=row[6] if len(row) > 6 else "Efectivo",
                )
            )
        return abonos
