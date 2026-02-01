🧾 SmartCredit App

SmartCredit App es una aplicación de escritorio hecha en Python para ayudar a gestionar un pequeño negocio de ventas a crédito, como una tienda de celulares u otros productos.

Este proyecto está pensado tanto para uso real como para aprendizaje, especialmente si estás empezando a programar y quieres ver cómo se construye una aplicación completa paso a paso.

No necesitas ser experto para entenderla 😊.

📌 ¿Qué hace esta aplicación?

Con SmartCredit puedes:

👤 Registrar y gestionar clientes

📦 Administrar inventario (productos y stock)

💰 Realizar ventas (al contado o a crédito)

💳 Registrar pagos

🔔 Enviar y mostrar notificaciones

🧾 Guardar todo en una base de datos local (SQLite)

Es una app de escritorio, no es web, y funciona directamente en tu computadora.

🛠️ Tecnologías usadas

Python 3

Tkinter + CustomTkinter → interfaz gráfica (ventanas, botones, formularios)

SQLite → base de datos local (un solo archivo)

Pillow → manejo de imágenes

PyInstaller → crear un ejecutable (.exe)

Logging → registro de errores y eventos

Todo está pensado para ser simple, estable y fácil de entender.

🧠 Cómo está organizada la aplicación

El código está organizado usando una arquitectura en capas, similar a MVC, pero simplificada.

📁 app/
🖥️ UI (Interfaz de Usuario) – app/ui

Aquí están las pantallas y componentes visuales.

main_window.py → ventana principal

views/

customer_view.py → clientes

inventory_view.py → inventario

sales_view.py → ventas

components/

top_bar.py → barra superior

toast.py → mensajes emergentes

styles.py → colores, fuentes y estilos

🧠 Servicios (Lógica de negocio) – app/services

Aquí vive el “cerebro” de la aplicación.

customer_service.py → manejo de clientes

inventory_service.py → productos y stock

sales_service.py → ventas

payment_service.py → pagos y créditos

notification_service.py → notificaciones

config_service.py → configuración global

📦 Modelos (Datos) – app/models

Definen la forma de los datos.

cliente.py

venta.py

telefono.py

dtos.py (objetos para transferir datos)

🗄️ Base de Datos – database.py

Usa SQLite

Implementa un Singleton (una sola conexión)

Usa ruta absoluta, evitando que se creen múltiples bases de datos

Maneja transacciones (si algo falla, no se guardan cambios)

📍 La base de datos se guarda siempre en una ruta fija del sistema, no depende de dónde se ejecute la app.

🧰 Utilidades – app/utils

logger.py → logs en smartcredit.log

enums.py → constantes (estados, tipos)

exceptions.py → errores personalizados

🚀 Cómo ejecutar la app (modo desarrollo)
Requisitos

Python 3.x instalado

Instalar dependencias:

pip install -r requirements.txt

Ejecutar la aplicación
python main.py


Se abre la ventana principal

La base de datos se crea automáticamente si no existe

Los logs se guardan en smartcredit.log

🧪 Pruebas

Para ejecutar las pruebas unitarias:

python -m unittest test_refactor.py


Esto sirve para validar que las partes críticas siguen funcionando correctamente.

📦 Crear el ejecutable (.exe)

Para generar un ejecutable usando PyInstaller:

python build.py


Se genera una carpeta dist/ o build/

El ejecutable puede usarse sin instalar Python

Ideal para distribución

⚠️ Reglas importantes (por favor leer)

❌ No versionar archivos .db

❌ No eliminar transacciones ni logging

❌ No cambiar la ruta de la base de datos sin entender el impacto

✅ Siempre cerrar conexiones a la base de datos

✅ Mantener la separación UI / Services / Database

👶 Consejos si eres principiante

Empieza por main.py, es el punto de entrada

Luego mira main_window.py

No tengas miedo de usar print() o el logger

Si algo falla, revisa:

Dependencias instaladas

smartcredit.log

Que la base de datos exista

Este proyecto es una excelente base para aprender cómo se construye una app real en Python.

🤝 Contribuciones y mejoras

Las mejoras son bienvenidas:

Nuevas vistas

Mejoras visuales

Optimización de experiencia de usuario

Más pruebas

Siempre respetando la arquitectura existente.

📄 Licencia

Este proyecto es de uso educativo y personal.
Puedes adaptarlo y aprender de él libremente.

