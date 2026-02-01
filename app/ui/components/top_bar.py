import customtkinter as ctk
from app.ui.styles import AppColors
from app.services.notification_service import NotificationService
from app.ui.views.notifications_view import NotificationsView


class TopBar(ctk.CTkFrame):
    def __init__(self, master, tasa_var, margen_var, **kwargs):
        super().__init__(master, height=60, corner_radius=0, **kwargs)
        self.tasa_var = tasa_var
        self.margen_var = margen_var
        self.notification_service = NotificationService()

        self._init_ui()
        self.check_notifications()  # Check on init

    def _init_ui(self):
        # Logo / Title Area
        title_label = ctk.CTkLabel(self, text="SmartCredit POS", font=("Arial", 22, "bold"))
        title_label.pack(side="left", padx=20, pady=10)

        # Status Wrapper (Right Side)
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(side="right", padx=20, pady=10)

        # Tasa Input
        self._create_setting(status_frame, "Tasa (Bs):", self.tasa_var, rx=r"^\d*\.?\d*$")

        # Spacer
        ctk.CTkFrame(status_frame, width=20, height=1, fg_color="transparent").pack(side="left")

        # Margen Input
        self._create_setting(status_frame, "Margen (%):", self.margen_var, rx=r"^\d*$")

        # Notifications Button
        self.btn_notif = ctk.CTkButton(
            status_frame,
            text="🔔",
            width=40,
            fg_color=AppColors.BG_CARD,
            text_color=AppColors.TEXT_PRIMARY,
            command=self.show_notifications,
        )
        self.btn_notif.pack(side="left", padx=10)

        # System Status Text
        self.lbl_status = ctk.CTkLabel(
            status_frame, text="🟢 SISTEMA ACTIVO", font=("Arial", 10, "bold"), text_color=AppColors.PRIMARY
        )
        self.lbl_status.pack(side="left", padx=(10, 0))

    def check_notifications(self):
        # Quick check to update icon color & badge
        # Rule: Only count urgent items (Today + Tomorrow)
        try:
            count = self.notification_service.get_urgent_badge_count()

            if count > 0:
                self.btn_notif.configure(fg_color=AppColors.DANGER, text=f"🔔 {count}", text_color="white", width=60)
            else:
                self.btn_notif.configure(
                    fg_color=AppColors.BG_CARD, text="🔔", text_color=AppColors.TEXT_PRIMARY, width=40
                )
        except Exception as e:
            print(f"Error checking notifications: {e}")

    def show_notifications(self):
        NotificationsView(self)
        # Refresh badge after closing? Idealmente sí, pero por ahora en init/timer
        # self.check_notifications()

    def _create_setting(self, parent, label, variable, rx):
        container = ctk.CTkFrame(parent, fg_color=AppColors.BG_CARD, corner_radius=6)
        container.pack(side="left", padx=5)

        ctk.CTkLabel(container, text=label, font=("Arial", 12, "bold"), text_color=AppColors.TEXT_SECONDARY).pack(
            side="left", padx=10
        )

        entry = ctk.CTkEntry(
            container,
            textvariable=variable,
            width=80,
            font=("Arial", 14, "bold"),
            border_width=0,
            fg_color="transparent",
        )
        entry.pack(side="left", padx=5)
