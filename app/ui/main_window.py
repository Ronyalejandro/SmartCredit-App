import customtkinter as ctk
from app.ui.views.inventory_view import InventoryView
from app.ui.views.customer_view import CustomerView
from app.ui.views.sales_view import SalesView
from app.ui.views.pos_view import POSView  # New POS View
from app.ui.components.top_bar import TopBar  # New TopBar
from app.services.config_service import ConfigService


class MainWindow(ctk.CTk):
    """
    Ventana principal de la aplicación SmartCredit.

    Gestiona la interfaz de usuario principal con pestañas para diferentes vistas:
    Venta, Inventario, Clientes y Historial de Ventas.
    """

    def __init__(self):
        super().__init__()

        self.title("SmartCredit")
        self.geometry("1200x800")
        self.minsize(1024, 768)

        # Theme configuration
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Config Service
        self.config_service = ConfigService()

        # Global Variables (Observables) - Initialized from Config
        self.tasa_cambio = ctk.StringVar(value=self.config_service.get_tasa())
        self.margen_ganancia = ctk.StringVar(value=self.config_service.get_margen())

        # Bind changes to save config
        self.tasa_cambio.trace_add("write", self._on_config_change)
        self.margen_ganancia.trace_add("write", self._on_config_change)

        self.views = {}

        self._init_ui()

    def _on_config_change(self, *args):
        # Update config service when UI variables change
        self.config_service.set_tasa(self.tasa_cambio.get())
        self.config_service.set_margen(self.margen_ganancia.get())

    def _init_ui(self):
        # 1. Top Bar (Global State)
        self.top_bar = TopBar(self, self.tasa_cambio, self.margen_ganancia)
        self.top_bar.pack(side="top", fill="x", padx=0, pady=0)

        # 2. Main Tab View (Navigation)
        self.tab_view = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tab_view.pack(side="top", fill="both", expand=True, padx=20, pady=(10, 20))

        # Define Tabs
        # "Punto de Venta" replaces "Financiamiento" as the main operational screen
        self.tab_pos = self.tab_view.add("Venta")
        self.tab_inventory = self.tab_view.add("Inventario")
        self.tab_customers = self.tab_view.add("Clientes")
        self.tab_sales = self.tab_view.add("Historial Ventas")

        # 3. Initialize Views
        # POS (Main)
        self.pos_view = POSView(self.tab_pos, self.tasa_cambio, self.margen_ganancia)
        self.pos_view.pack(fill="both", expand=True)
        self.views["Punto de Venta"] = self.pos_view

        # Inventario
        # Pasamos callback para que InventoryView notifique cambios a POSView
        self.inventory_view = InventoryView(self.tab_inventory, on_change=self.pos_view.refresh_products)
        self.inventory_view.pack(fill="both", expand=True)
        self.views["Inventario"] = self.inventory_view

        # Clientes
        # Pasamos callback para que CustomerView notifique cambios a POSView
        self.customer_view = CustomerView(self.tab_customers, on_change=self.pos_view.load_data)
        self.customer_view.pack(fill="both", expand=True)
        self.views["Clientes"] = self.customer_view

        # Historial Ventas
        self.sales_view = SalesView(self.tab_sales)
        self.sales_view.pack(fill="both", expand=True)
        self.views["Historial Ventas"] = self.sales_view

        # Set Default Tab
        self.tab_view.set("Venta")

    def on_tab_change(self):
        # Smart refresh logic
        current_tab = self.tab_view.get()
        if current_tab in self.views:
            view = self.views[current_tab]
            # Duck typing check: if view has 'refresh_list' or 'load_data', call it
            if hasattr(view, "refresh_list"):
                view.refresh_list()
            elif hasattr(view, "load_data"):
                view.load_data()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
