# Copilot / AI agent instructions for SmartCredit App

Resumen breve
- Proyecto GUI de escritorio (Tkinter / CustomTkinter) con lógica centralizada en servicios y una base SQLite local (`smartcredit.db`). Ejecuta con `python main.py`; empaqueta con `python build.py` (usa PyInstaller).

Arquitectura (big picture)
- UI: `app/ui/` — ventanas, vistas y componentes; `MainWindow` inicia el `mainloop` (ver [main.py](main.py)).
- Servicios: `app/services/` — encapsulan lógica de negocio y acceso a datos (ej: `ServicioClientes`, `ServiceInventario`, `ServiceVentas`).
- Modelos: `app/models/` — objetos ligeros con fábrica `from_row` (ej: [app/models/cliente.py](app/models/cliente.py)).
- Persistencia: `app/db/database.py` — singleton que inicializa tablas y expone `get_connection()` (SQLite). Cerrar conexiones y usar commit/rollback según patrón del servicio.
- Logging: `app/utils/logger.py` — logger global `SmartCredit` con rotación en `smartcredit.log`.

Patrones y convenciones de este repo
- Base de datos: cada servicio obtiene `conn = Database().get_connection()`, crea cursor, commit/rollback y siempre `conn.close()` en `finally`. Mantener ese patrón para consistencia.
- Transacciones: operaciones que modifican stock/ventas deben ser atómicas en el servicio (ver `test_refactor.py` que espera decremento de stock tras `procesar_venta`).
- Model factories: usar `Model.from_row(row)` al transformar filas SQL a objetos.
- Nombres en español: clases, métodos y mensajes usan español (p. ej. `ServicioClientes.registrar_cliente`). Mantener idioma para variables públicas y logs.

Flujos de desarrollo y comandos relevantes
- Ejecutar la app en desarrollo: `python main.py` (crea `smartcredit.db` si no existe). Logs en `smartcredit.log`.
- Tests (unidad básica incluida): `python -m unittest` o `python -m unittest test_refactor.py`.
- Build / distribución: `python build.py` — instala PyInstaller si falta; genera ejecutable con `--hidden-import customtkinter` y `PIL._tkinter_finder`. Para ajustes directos, ver [build.py](build.py).
- Dependencias: declaradas en `requirements.txt` (`customtkinter`, `Pillow`, `pyinstaller`). Instalar con `pip install -r requirements.txt`.

Integraciones y puntos críticos
- Archivo DB: `smartcredit.db` vive en el cwd. No asumir concurrencia pesada (SQLite). Evitar operaciones largas en el hilo UI.
- Recursos estáticos: actualmente no hay carpeta `assets` formal; `build.py` muestra cómo añadir `--add-data` si se incorporan imágenes/archivos.

Ejemplos rápidos (cómo implementar cambios compatibles)
- Añadir nuevo servicio: crear `app/services/nuevo_servicio.py`, usar `Database()` y seguir commit/rollback y cierre de conexión. Registrar logs con `logging.getLogger("SmartCredit")`.
- Nueva tabla: agregar `CREATE TABLE IF NOT EXISTS` en `Database.init_db()` y versionar manualmente si necesitas migraciones.

Qué NO cambiar sin coordinación
- No mover `Database.DB_NAME` sin actualizar scripts de build/tests. No eliminar el patrón de cierre de conexiones en los servicios.

Archivos clave para revisar al trabajar aquí
- [main.py](main.py)
- [build.py](build.py)
- [requirements.txt](requirements.txt)
- [app/db/database.py](app/db/database.py)
- [app/services/](app/services/)
- [app/models/](app/models/)
- [app/utils/logger.py](app/utils/logger.py)
- [test_refactor.py](test_refactor.py)

Si necesitas más contexto
- Pide que extraiga flujos concretos (ej. proceso de venta completo) o que añada ejemplos de PRs/commits.

---
Por favor revisa este borrador y dime si quieres más ejemplos de código, añadir reglas de estilo o incluir pasos de CI/CD.
