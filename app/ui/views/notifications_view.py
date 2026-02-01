import customtkinter as ctk
from app.services.notification_service import NotificationService
from app.ui.styles import AppColors


class NotificationsView(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Centro de Notificaciones y Control de Créditos")
        self.geometry("800x600")
        self.attributes("-topmost", True)

        self.service = NotificationService()
        self.all_data = []  # Cache for client-side filtering
        self.filtered_data = []

        self._init_ui()
        self.load_data()

    def _init_ui(self):
        # --- Header ---
        header = ctk.CTkFrame(self, height=50, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(header, text="Control de Créditos", font=("Arial", 20, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Cerrar", width=80, fg_color="gray", command=self.destroy).pack(side="right")

        # --- Filter Bar ---
        filter_frame = ctk.CTkFrame(self, fg_color=AppColors.BG_CARD)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Search Client
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_filter_change)
        ctk.CTkLabel(filter_frame, text="🔍 Cliente:", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)
        ctk.CTkEntry(filter_frame, textvariable=self.search_var, width=200, placeholder_text="Nombre...").pack(
            side="left", padx=5
        )

        # Status Filter
        self.status_var = ctk.StringVar(value="Todos")
        ctk.CTkLabel(filter_frame, text="Estado:", font=("Arial", 12, "bold")).pack(side="left", padx=(20, 10))
        self.combo_status = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.status_var,
            values=["Todos", "🟢 Al día", "🟠 Próximo", "🔴 Vencido"],
            command=self._on_filter_change,
        )
        self.combo_status.pack(side="left", padx=5)

        # Refresh
        ctk.CTkButton(filter_frame, text="🔄 Actualizar", width=80, command=self.load_data).pack(side="right", padx=10)

        # --- Content Area ---
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Listado de Créditos")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def load_data(self):
        # Fetch from service
        self.all_data = self.service.get_all_credits_status()
        self.apply_filters()

    def _on_filter_change(self, *args):
        self.apply_filters()

    def apply_filters(self):
        search_term = self.search_var.get().lower()
        status_filter = self.status_var.get()

        self.filtered_data = []
        for item in self.all_data:
            # Filter by Name
            if search_term and search_term not in item.cliente_nombre.lower():
                continue

            # Filter by Status
            if status_filter != "Todos" and item.estado_etiqueta != status_filter:
                continue

            self.filtered_data.append(item)

        self.render_list()

    def render_list(self):
        # Clear current
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.filtered_data:
            ctk.CTkLabel(self.scroll, text="No se encontraron créditos con estos filtros.", text_color="gray").pack(
                pady=40
            )
            return

        # Sort: Vencidos first, then Proximos, then Al dia
        # Simple custom sort key: Vencido=0, Proximo=1, Al dia=2
        def sort_key(item):
            if "Vencido" in item.estado_etiqueta:
                return 0
            if "Próximo" in item.estado_etiqueta:
                return 1
            return 2

        self.filtered_data.sort(key=sort_key)

        for item in self.filtered_data:
            self._create_card(item)

    def _create_card(self, item):
        # Determine Color based on status
        border_color = AppColors.BG_CARD
        if "Vencido" in item.estado_etiqueta:
            border_color = AppColors.DANGER
        elif "Próximo" in item.estado_etiqueta:
            border_color = AppColors.WARNING

        card = ctk.CTkFrame(self.scroll, fg_color=AppColors.BG_CARD, border_width=1, border_color=border_color)
        card.pack(fill="x", pady=5, padx=5)

        # Column 1: Client & Product
        col1 = ctk.CTkFrame(card, fg_color="transparent")
        col1.pack(side="left", padx=10, pady=10, fill="y")

        ctk.CTkLabel(col1, text=item.cliente_nombre, font=("Arial", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(col1, text=item.producto_nombre, font=("Arial", 12), text_color="gray").pack(anchor="w")

        # Column 2: Status & Debt Info
        col2 = ctk.CTkFrame(card, fg_color="transparent")
        col2.pack(side="left", padx=20, pady=10, fill="y")

        status_color = AppColors.TEXT_PRIMARY
        if "Vencido" in item.estado_etiqueta:
            status_color = AppColors.DANGER
        elif "Próximo" in item.estado_etiqueta:
            status_color = AppColors.WARNING
        elif "Al día" in item.estado_etiqueta:
            status_color = AppColors.SUCCESS

        ctk.CTkLabel(col2, text=item.estado_etiqueta, font=("Arial", 12, "bold"), text_color=status_color).pack(
            anchor="w"
        )

        detail_text = f"Prox. Cuota: {item.proxima_cuota_fecha} (${item.proxima_cuota_monto:.2f})"
        if item.dias_mora > 0:
            detail_text += f" | {item.dias_mora} días mora"

        ctk.CTkLabel(col2, text=detail_text, font=("Arial", 11)).pack(anchor="w")

        # Column 3: Total Balance
        col3 = ctk.CTkFrame(card, fg_color="transparent")
        col3.pack(side="left", padx=20, pady=10, fill="y")

        ctk.CTkLabel(col3, text="Saldo Total", font=("Arial", 10), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(col3, text=f"${item.saldo_pendiente_usd:.2f}", font=("Arial", 14, "bold")).pack(anchor="w")

        # Column 4: Actions
        col4 = ctk.CTkFrame(card, fg_color="transparent")
        col4.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(
            col4,
            text="📋 Mensaje",
            width=100,
            height=30,
            fg_color=AppColors.INFO,
            command=lambda m=item.mensaje_sugerido: self.copy_to_clipboard(m),
        ).pack(side="right")

    def copy_to_clipboard(self, message):
        self.clipboard_clear()
        self.clipboard_append(message)
        self.update()

        # Visual feedback
        try:
            from app.ui.components.toast import ToastNotification

            ToastNotification(self, "Copiado", "Mensaje listo para pegar.", color="blue")
        except Exception:
            pass
