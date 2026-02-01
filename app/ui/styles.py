"""
Centralización de estilos y constantes visuales (Design Tokens).
Permite cambios globales de tema y asegura consistencia visual.
"""


class AppColors:
    # Colores de Marca (Brand Colors)
    PRIMARY = "#2ec4b6"  # Teal vibrante - Acciones principales, éxito
    DANGER = "#e63946"  # Rojo - Errores, cancelar, eliminar
    WARNING = "#ff9f1c"  # Naranja - Alertas de stock
    SUCCESS = "#2ec4b6"  # Verde/Teal - Estado OK
    INFO = "#3a86ff"  # Azul - Información neutral
    ACCENT = PRIMARY  # Alias para PRIMARY

    # Colores Adaptativos (Light Mode, Dark Mode)
    # CustomTkinter usa tuplas ("color_light", "color_dark")

    # Fondos
    BG_MAIN = ("gray98", "#121212")  # Fondo principal de ventanas
    BG_PANEL = ("gray90", "#1e1e1e")  # Paneles laterales / contenedores
    BG_CARD = ("#ffffff", "#2d2d2d")  # Tarjetas de productos
    BG_INPUT = ("#ffffff", "#333333")  # Campos de entrada

    # Textos
    TEXT_PRIMARY = ("#1a1a1a", "#eeeeee")  # Títulos, valores importantes
    TEXT_SECONDARY = ("#666666", "#aaaaaa")  # Etiquetas, subtítulos
    TEXT_INVERTED = ("#ffffff", "#000000")  # Texto sobre botones sólidos


class AppFonts:
    # Tipografías estándar
    TITLE = ("Arial", 22, "bold")
    SUBTITLE = ("Arial", 16, "bold")
    BODY = ("Arial", 12)
    SMALL = ("Arial", 10)

    # Números grandes (Precios)
    PRICE_LARGE = ("Arial", 40, "bold")
    PRICE_MEDIUM = ("Arial", 18, "bold")
