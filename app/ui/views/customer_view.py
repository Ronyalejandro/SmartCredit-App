import customtkinter as ctk
from tkinter import messagebox
from app.services.customer_service import ServicioClientes
from app.services.payment_service import PaymentService
from app.services.sales_service import ServiceVentas  # Para historial detallado
from app.ui.styles import AppColors, AppFonts
from app.utils.exceptions import BusinessRuleError


class CustomerView(ctk.CTkFrame):
    def __init__(self, master, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.service = ServicioClientes()
        # Optional callback to notify other views about customer changes
        self.on_change = on_change
        self.payment_service = PaymentService()
        self.sales_service = ServiceVentas()
        self.abonos_visible = {}  # Store visibility state for abonos details

        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        # Layout: Left side (List), Right side (Form)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Left Side: Customer List ---
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Lista de Clientes")
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Right Side: Form ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.form_frame, text="Registrar Cliente", font=("Arial", 16, "bold")).pack(pady=10)

        # Fields
        self.entry_nombre = self._create_input("Nombre Completo")
        self.entry_cedula = self._create_input("Cédula / ID")
        self.entry_telefono = self._create_input("Teléfono de Contacto")

        # Action Buttons
        button_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_container.pack(pady=20, fill="x")

        ctk.CTkButton(
            button_container, text="Guardar Cliente", command=self.save_customer, fg_color=AppColors.PRIMARY
        ).pack(fill="x", pady=5)
        ctk.CTkButton(button_container, text="Limpiar", command=self.clear_form, fg_color="gray").pack(fill="x", pady=5)

    def _create_input(self, label):
        ctk.CTkLabel(self.form_frame, text=label).pack(pady=(10, 0))
        entry = ctk.CTkEntry(self.form_frame)
        entry.pack(pady=5)
        return entry

    def save_customer(self):
        nombre = self.entry_nombre.get()
        cedula = self.entry_cedula.get()
        telefono = self.entry_telefono.get()

        if not nombre or not cedula:
            messagebox.showerror("Error", "Nombre y Cédula son obligatorios")
            return

        try:
            self.service.registrar_cliente(nombre, cedula, telefono)
            self.refresh_list()
            # Notify other views (e.g., POS) that clients changed
            try:
                if callable(self.on_change):
                    self.on_change()
            except Exception:
                pass
            self.clear_form()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.entry_nombre.delete(0, "end")
        self.entry_cedula.delete(0, "end")
        self.entry_telefono.delete(0, "end")

    def refresh_list(self):
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        customers = self.service.obtener_todos_clientes()

        for c in customers:
            self._create_customer_card(c)

        # Force UI update
        self.list_frame.update_idletasks()

    def _create_customer_card(self, customer):
        card = ctk.CTkFrame(self.list_frame, fg_color=("gray85", "gray25"))
        card.pack(fill="x", pady=5, padx=5)

        info_text = f"{customer.nombre}\nCedula: {customer.cedula} | Tlf: {customer.telefono}"
        ctk.CTkLabel(card, text=info_text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)

        ctk.CTkButton(
            card,
            text="Estado de Cuenta",
            width=120,
            font=("Arial", 11, "bold"),
            fg_color=AppColors.INFO,
            command=lambda c_id=customer.id, c_name=customer.nombre: self.show_account_status(c_id, c_name),
        ).pack(side="right", padx=10)

    def show_account_status(self, customer_id, customer_name):
        history = self.sales_service.obtener_historial_ventas(customer_id)

        top = ctk.CTkToplevel(self)
        top.title(f"Estado de Cuenta: {customer_name}")
        top.geometry("700x500")
        top.attributes("-topmost", True)  # Improvement: Keep window on top for focus

        # Container
        scroll = ctk.CTkScrollableFrame(top, label_text="Ventas y Créditos Activos")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        if not history:
            ctk.CTkLabel(scroll, text="No hay movimientos registrados.").pack(pady=20)
            return

        for row in history:
            # Row structure from query: id, fecha, c.nombre, t.nombre, tipo, precio, saldo
            v_id, fecha, _, prod_name, tipo, precio, saldo = row

            card = ctk.CTkFrame(scroll, fg_color=AppColors.BG_CARD)
            card.pack(fill="x", pady=5, padx=5)

            # Info Column
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=10, pady=10)

            ctk.CTkLabel(info_frame, text=f"{prod_name} ({tipo})", font=AppFonts.BODY).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Fecha: {fecha}", font=("Arial", 10), text_color="gray").pack(anchor="w")

            # Financial Column
            fin_frame = ctk.CTkFrame(card, fg_color="transparent")
            fin_frame.pack(side="right", padx=10, pady=10)

            ctk.CTkLabel(fin_frame, text=f"Total: ${precio:.2f}", font=("Arial", 11)).pack(anchor="e")

            lbl_saldo = ctk.CTkLabel(
                fin_frame,
                text=f"Deuda: ${saldo:.2f}",
                font=("Arial", 12, "bold"),
                text_color=AppColors.DANGER if saldo > 0 else AppColors.PRIMARY,
            )
            lbl_saldo.pack(anchor="e")

            # Actions
            # Actions and Details
            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.pack(fill="x", padx=10, pady=(0, 10))

            if saldo > 0:
                ctk.CTkButton(
                    action_frame,
                    text="💰 ABONAR",
                    height=24,
                    width=80,
                    fg_color="#2a9d8f",
                    command=lambda vid=v_id, sal=saldo: self.open_payment_dialog(vid, sal, top),
                ).pack(side="right", padx=5)

            # Toggle Abonos Button
            ctk.CTkButton(
                action_frame,
                text="Ver Pagos",
                height=24,
                width=80,
                fg_color="gray",
                command=lambda vid=v_id, c=card: self.toggle_abonos(vid, c),
            ).pack(side="right", padx=5)

    def toggle_abonos(self, venta_id, parent_card):
        # Check if already open (simple naive check via checking children or explicit tracking)
        # Better: use a frame container inside parent_card dedicated for details

        # Check if details frame already exists
        details_frame_name = f"details_{venta_id}"

        # Look for existing frame
        existing = None
        for child in parent_card.winfo_children():
            if getattr(child, "name_id", "") == details_frame_name:
                existing = child
                break

        if existing:
            existing.destroy()
            return

        # Create Details Frame
        details = ctk.CTkFrame(parent_card, fg_color=("gray90", "gray20"))
        details.name_id = details_frame_name
        details.pack(fill="x", padx=10, pady=5)

        abonos = self.payment_service.obtener_abonos_por_venta(venta_id)

        if not abonos:
            ctk.CTkLabel(details, text="No hay abonos registrados.", font=("Arial", 10, "italic")).pack(pady=5)
        else:
            ctk.CTkLabel(details, text="Historial de Pagos:", font=("Arial", 10, "bold")).pack(
                anchor="w", padx=5, pady=2
            )
            for abono in abonos:
                row = ctk.CTkFrame(details, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{abono.fecha}", width=120, anchor="w", font=("Arial", 10)).pack(side="left")
                ctk.CTkLabel(
                    row, text=f"${abono.monto_usd:.2f}", width=60, anchor="e", font=("Arial", 10, "bold")
                ).pack(side="left")
                ctk.CTkLabel(
                    row, text=f"(Bs {abono.monto_bs:.2f} @ {abono.tasa_cambio})", font=("Arial", 10), text_color="gray"
                ).pack(side="left", padx=5)

    def open_payment_dialog(self, venta_id, saldo_actual, parent_window):
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title("Registrar Abono")
        dialog.geometry("300x350")
        dialog.attributes("-topmost", True)  # Ensure dialog is above the topmost parent

        ctk.CTkLabel(dialog, text="Monto a Abonar (USD):").pack(pady=(20, 5))
        entry_amount = ctk.CTkEntry(dialog)
        entry_amount.pack(pady=5)

        ctk.CTkLabel(dialog, text="Tasa del Día (Bs):").pack(pady=(10, 5))
        entry_rate = ctk.CTkEntry(dialog)
        entry_rate.pack(pady=5)

        # Default Rate (Could be fetched from global state if passed, simplest is manual or standard)
        entry_rate.insert(0, "40.0")

        ctk.CTkLabel(dialog, text=f"Saldo Pendiente: ${saldo_actual:.2f}", text_color=AppColors.DANGER).pack(pady=10)

        ctk.CTkLabel(dialog, text="Método de Pago:").pack(pady=(5, 0))
        cmb_method = ctk.CTkComboBox(dialog, values=["Efectivo", "Pago Móvil", "Zelle", "Transferencia"])
        cmb_method.pack(pady=5)
        cmb_method.set("Efectivo")

        def confirm():
            try:
                monto = float(entry_amount.get())
                tasa = float(entry_rate.get())
                metodo = cmb_method.get()

                self.payment_service.registrar_abono(venta_id, monto, tasa, metodo, "Abono Manual")

                # Toast Feedback
                from app.ui.components.toast import ToastNotification

                ToastNotification(parent_window, "Abono Exitoso", f"Abono de ${monto} registrado ({metodo}).")

                dialog.destroy()
                # Refresh logic? Ideally refresh parent list or close top
                # parent_window is 'top' (Account Status)
                # We should refresh the list inside 'top'.
                # For now, closing 'top' is safest to force refresh when reopening.
                parent_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
            except BusinessRuleError as e:
                messagebox.showerror("Error de Negocio", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Confirmar Abono", command=confirm, fg_color=AppColors.PRIMARY).pack(pady=20)
