import customtkinter as ctk
from app.services.sales_service import ServiceVentas
from app.ui.styles import AppColors


class SalesView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.service = ServiceVentas()

        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header_frame, text="Historial General de Ventas", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(
            header_frame, text="Actualizar", command=self.refresh_list, width=100, fg_color=AppColors.ACCENT
        ).pack(side="right", padx=10)

        # Table Header
        self.table_header = ctk.CTkFrame(self, fg_color="gray30", height=40)
        self.table_header.pack(fill="x", padx=10)

        cols = ["Fecha", "Cliente", "Equipo", "Tipo", "Precio Final", "Deuda Pendiente"]
        widths = [150, 150, 150, 100, 100, 100]

        for col, w in zip(cols, widths):
            ctk.CTkLabel(self.table_header, text=col, width=w, font=("Arial", 12, "bold")).pack(side="left", padx=5)

        # Scrollable List
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_list(self):
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        sales = self.service.obtener_historial_ventas()

        # sales row: id, fecha, nom_cliente, nom_telf, tipo, precio, saldo

        widths = [150, 150, 150, 100, 100, 100]

        for s in sales:
            row_frame = ctk.CTkFrame(self.list_frame, fg_color=("gray85", "gray25"))
            row_frame.pack(fill="x", pady=2)

            # Data from s[1] onwards (skip id for display)
            data_points = [s[1], s[2], s[3], s[4], f"${s[5]:.2f}", f"${s[6]:.2f}"]

            for data, w in zip(data_points, widths):
                ctk.CTkLabel(row_frame, text=data, width=w, anchor="center").pack(side="left", padx=5)
