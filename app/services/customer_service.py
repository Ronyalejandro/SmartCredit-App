from app.db.database import Database
from app.models.cliente import Cliente
import logging

logger = logging.getLogger("SmartCredit")


class ServicioClientes:
    def __init__(self):
        self.db = Database()

    def registrar_cliente(self, nombre, cedula, telefono):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO clientes (nombre, cedula, telefono)
                VALUES (?, ?, ?)
            """,
                (nombre, cedula, telefono),
            )
            conn.commit()
            logger.info(f"Cliente registrado: {nombre} (Cédula: {cedula})")
        except Exception as e:
            logger.error(f"Error al registrar cliente: {e}")
            conn.rollback()
            raise ValueError(f"Error al registrar cliente: {e}")
        finally:
            conn.close()

    def obtener_todos_clientes(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nombre ASC")
        rows = cursor.fetchall()
        conn.close()
        return [Cliente.from_row(row) for row in rows]

    def obtener_cliente_por_id(self, customer_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return Cliente.from_row(row) if row else None

    def obtener_historial_cliente(self, customer_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT v.fecha, t.nombre, v.tipo_venta, v.precio_final_usd
            FROM ventas v
            JOIN inventario t ON v.id_telefono = t.id
            WHERE v.id_cliente = ?
            ORDER BY v.fecha DESC
        """,
            (customer_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
