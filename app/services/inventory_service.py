from app.db.database import Database
from app.models.telefono import Telefono
import logging

logger = logging.getLogger("SmartCredit")


class ServiceInventario:
    def __init__(self):
        self.db = Database()

    def agregar_telefono(self, nombre, costo_original_usd, stock, ruta_imagen):
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO inventario (nombre, costo_original_usd, stock, ruta_imagen)
                VALUES (?, ?, ?, ?)
            """,
                (nombre, costo_original_usd, stock, ruta_imagen),
            )
            conn.commit()
            logger.info(f"Teléfono registrado: {nombre} (Stock: {stock}, Costo: ${costo_original_usd})")
        except Exception as e:
            logger.error(f"Error al registrar teléfono: {e}")
            conn.rollback()
            raise ValueError(f"Error al registrar teléfono: {e}")
        finally:
            conn.close()

    def obtener_todos_telefonos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario ORDER BY nombre ASC")
        rows = cursor.fetchall()
        conn.close()
        return [Telefono.from_row(row) for row in rows]

    def obtener_telefono_por_id(self, phone_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE id = ?", (phone_id,))
        row = cursor.fetchone()
        conn.close()
        return Telefono.from_row(row) if row else None

    def actualizar_telefono(self, phone_id, nombre, costo_original_usd, stock, ruta_imagen):
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE inventario
                SET nombre = ?, costo_original_usd = ?, stock = ?, ruta_imagen = ?
                WHERE id = ?
            """,
                (nombre, costo_original_usd, stock, ruta_imagen, phone_id),
            )
            conn.commit()
        finally:
            conn.close()

    def eliminar_telefono(self, phone_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM inventario WHERE id = ?", (phone_id,))
            conn.commit()
        finally:
            conn.close()

    def actualizar_stock(self, phone_id, cambio_cantidad, cursor=None):
        """
        Actualiza el stock de un producto.

        Args:
            phone_id: ID del teléfono
            cambio_cantidad: Cantidad a sumar (positivo) o restar (negativo)
            cursor: Cursor de base de datos opcional para transacciones externas.
                    Si es None, se crea una nueva conexión y se hace commit.
        """
        local_conn = None
        if cursor is None:
            local_conn = self.db.get_connection()
            cursor = local_conn.cursor()

        try:
            # Verificar stock actual dentro de la misma transacción (o auto-commit si es local)
            cursor.execute("SELECT stock FROM inventario WHERE id = ?", (phone_id,))
            row = cursor.fetchone()

            if not row:
                raise ValueError(f"Producto con ID {phone_id} no encontrado.")

            stock_actual = row[0]
            nuevo_stock = stock_actual + cambio_cantidad

            if nuevo_stock < 0:
                raise ValueError(
                    f"No hay suficiente stock disponible. Stock actual: {stock_actual}, "
                    f"Solicitado: {abs(cambio_cantidad)}"
                )

            cursor.execute("UPDATE inventario SET stock = ? WHERE id = ?", (nuevo_stock, phone_id))

            if local_conn:
                local_conn.commit()

        except Exception as e:
            if local_conn:
                local_conn.rollback()
            raise e
        finally:
            if local_conn:
                local_conn.close()

    def verificar_stock_bajo(self, umbral=5):
        """
        Retorna lista de teléfonos con stock menor o igual al umbral.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE stock <= ? ORDER BY stock ASC", (umbral,))
        rows = cursor.fetchall()
        conn.close()
        return [Telefono.from_row(row) for row in rows]

    def actualizar_stock_rapido(self, phone_id, cantidad_a_sumar):
        """
        Wrapper seguro para actualizaciones rápidas desde la UI (ej. botón +).
        """
        # Reutilizamos la lógica transaccional existente
        self.actualizar_stock(phone_id, cantidad_a_sumar)
