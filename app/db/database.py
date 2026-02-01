import sqlite3
import os


class Database:
    _instance = None
    # CHANGE: Ruta absoluta en %APPDATA%/SmartCredit/ para evitar múltiples BD
    # REASON: La ruta relativa causaba creación de BD en diferentes cwd (VS Code vs exe)
    DB_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'SmartCredit')
    DB_NAME = os.path.join(DB_DIR, 'smartcredit.db')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # CHANGE: Crear directorio si no existe
            # REASON: Garantizar que la carpeta existe antes de conectar
            os.makedirs(cls.DB_DIR, exist_ok=True)
            cls._instance.init_db()
        return cls._instance

    def get_connection(self):
        return sqlite3.connect(self.DB_NAME)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla Inventario (Telefonos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                costo_original_usd REAL NOT NULL,
                stock INTEGER NOT NULL,
                ruta_imagen TEXT
            )
        """)

        # Tabla Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT UNIQUE NOT NULL,
                telefono TEXT
            )
        """)

        # Tabla Ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                id_telefono INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                tipo_venta TEXT NOT NULL,
                precio_final_usd REAL NOT NULL,
                pago_inicial_usd REAL,
                saldo_pendiente_usd REAL,
                cuotas_totales INTEGER,
                monto_cuota_usd REAL,
                tasa_cambio_usada REAL NOT NULL,
                estado TEXT NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id),
                FOREIGN KEY (id_telefono) REFERENCES inventario (id)
            )
        """)

        # Tabla Abonos (Pagos Parciales)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS abonos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                monto_usd REAL NOT NULL,
                tasa_cambio REAL NOT NULL,
                monto_bs REAL NOT NULL,
                notas TEXT,
                FOREIGN KEY (venta_id) REFERENCES ventas (id)
            )
        """)

        # Tabla Cuotas (Plan de Pagos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cuotas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                numero_cuota INTEGER NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                monto_usd REAL NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente',
                FOREIGN KEY (venta_id) REFERENCES ventas (id)
            )
        """)

        conn.commit()
        conn.close()
