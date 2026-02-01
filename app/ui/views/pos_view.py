import customtkinter as ctk
from PIL import Image
from app.services.inventory_service import ServiceInventario
from app.services.sales_service import ServiceVentas
from app.services.customer_service import ServicioClientes
from tkinter import messagebox
import os
from app.utils.exceptions import BusinessRuleError, InventoryError, SmartCreditError
from app.ui.styles import AppColors


class POSView(ctk.CTkFrame):
    def __init__(self, master, tasa_var, margen_var, **kwargs):
        super().__init__(master, **kwargs)

        # Services & State
        self.tasa_var = tasa_var
        self.margen_var = margen_var

        self.s_inv = ServiceInventario()
        self.s_ventas = ServiceVentas()
        self.s_clientes = ServicioClientes()

        # Selection State
        self.selected_phone = None
        self.selected_client_id = None
        self.customers_map = {}

        # UI Listeners
        self.tasa_var.trace_add("write", self.update_calculations)
        self.margen_var.trace_add("write", self.update_calculations)

        self._init_layout()
        self.load_data()

    def _init_layout(self):
        self.columnconfigure(0, weight=2)  # Cart
        self.columnconfigure(1, weight=5)  # Catalog
        self.columnconfigure(2, weight=2)  # Totals
        self.rowconfigure(0, weight=1)

        # === 1. LEFT: CART & CONTEXT ===
        self.left_panel = ctk.CTkFrame(self, fg_color=AppColors.BG_PANEL)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        ctk.CTkLabel(self.left_panel, text="CLIENTE", font=("Arial", 12, "bold"), text_color="gray").pack(
            pady=(10, 0), padx=10, anchor="w"
        )
        self.combo_client = ctk.CTkComboBox(self.left_panel, command=self.on_client_select)
        self.combo_client.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.left_panel, text="DETALLE PRODUCTO", font=("Arial", 12, "bold"), text_color="gray").pack(
            pady=(20, 0), padx=10, anchor="w"
        )
        self.lbl_prod_name = ctk.CTkLabel(self.left_panel, text="Ninguno", font=("Arial", 16))
        self.lbl_prod_name.pack(padx=10, anchor="w")

        self.lbl_stock_status = ctk.CTkLabel(self.left_panel, text="--", font=("Arial", 10))
        self.lbl_stock_status.pack(padx=10, anchor="w")

        # Payment Inputs
        ctk.CTkLabel(self.left_panel, text="CONDICIONES PAGO", font=("Arial", 12, "bold"), text_color="gray").pack(
            pady=(20, 0), padx=10, anchor="w"
        )

        self.lbl_payment_initial_label = ctk.CTkLabel(self.left_panel, text="Inicial ($):")
        self.lbl_payment_initial_label.pack(padx=10, anchor="w")

        # Validation for Entry
        vcmd = (self.register(self.validate_number), "%P")
        self.entry_initial = ctk.CTkEntry(self.left_panel, validate="key", validatecommand=vcmd)
        self.entry_initial.pack(fill="x", padx=10, pady=2)
        self.entry_initial.bind("<KeyRelease>", self.update_calculations)

        ctk.CTkLabel(self.left_panel, text="Cuotas:").pack(padx=10, anchor="w", pady=(5, 0))
        self.combo_installments = ctk.CTkComboBox(
            self.left_panel, values=["0 (Contado)", "3", "4", "5", "6"], command=self.update_calculations
        )
        self.combo_installments.set("3")
        self.combo_installments.pack(fill="x", padx=10, pady=2)

        # === 2. CENTER: CATALOG ===
        self.center_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.catalog_scroll = ctk.CTkScrollableFrame(self.center_panel, label_text="Catálogo de Productos")
        self.catalog_scroll.pack(fill="both", expand=True)

        # === 3. RIGHT: TOTALS ===
        self.right_panel = ctk.CTkFrame(self, fg_color=AppColors.BG_PANEL)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        self.right_panel.columnconfigure(0, weight=1)

        # Big Numbers
        ctk.CTkLabel(self.right_panel, text="TOTAL A PAGAR", font=("Arial", 14)).pack(pady=(20, 5))
        self.lbl_total_usd = ctk.CTkLabel(
            self.right_panel, text="$0.00", font=("Arial", 40, "bold"), text_color=AppColors.PRIMARY
        )
        self.lbl_total_usd.pack()
        self.lbl_total_bs = ctk.CTkLabel(self.right_panel, text="Bs 0.00", font=("Arial", 16), text_color="gray")
        self.lbl_total_bs.pack()

        ctk.CTkFrame(self.right_panel, height=2, fg_color="gray").pack(fill="x", padx=20, pady=20)

        # Installment Detail
        self.info_installments_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.info_installments_frame.pack(fill="x", padx=10)

        self.lbl_installment_val = ctk.CTkLabel(
            self.info_installments_frame, text="Cuota: $0.00", font=("Arial", 18, "bold")
        )
        self.lbl_installment_val.pack()
        self.lbl_balance_val = ctk.CTkLabel(self.info_installments_frame, text="Saldo: $0.00", font=("Arial", 12))
        self.lbl_balance_val.pack()

        # Action Buttons
        self.spacer = ctk.CTkLabel(self.right_panel, text="")
        self.spacer.pack(expand=True)

        self.btn_process = ctk.CTkButton(
            self.right_panel,
            text="✅ PROCESAR",
            height=60,
            font=("Arial", 18, "bold"),
            fg_color=AppColors.PRIMARY,
            state="disabled",  # Disabled by default
            command=self.process_sale,
        )
        self.btn_process.pack(fill="x", padx=20, pady=10)

        self.btn_cancel = ctk.CTkButton(
            self.right_panel,
            text="❌ CANCELAR",
            height=40,
            fg_color=AppColors.DANGER,
            hover_color="#d62828",
            command=self.reset_selection,
        )
        self.btn_cancel.pack(fill="x", padx=20, pady=(0, 20))

    def validate_number(self, new_value):
        if not new_value:
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def load_data(self):
        # Refresh Clients
        clients = self.s_clientes.obtener_todos_clientes()
        self.customers_map = {c.nombre: c.id for c in clients}
        self.combo_client.configure(values=list(self.customers_map.keys()))
        if self.customers_map and not self.selected_client_id:
            self.combo_client.set(list(self.customers_map.keys())[0])
            self.on_client_select(list(self.customers_map.keys())[0])

        # Refresh Catalog
        self._populate_catalog()

    def refresh_products(self):
        """
        Reconsulta al ServiceInventario y actualiza el catálogo de productos
        en la UI sin reiniciar la aplicación.

        - Reutiliza la lógica de población del catálogo.
        - Si el producto actualmente seleccionado cambió (p. ej. update/delete),
          actualiza la selección o la limpia.
        """
        # Re-populate catalog (this will query the DB again)
        self._populate_catalog()

        # If we had a selected product, refresh its data from DB
        if self.selected_phone:
            try:
                fresh = self.s_inv.obtener_telefono_por_id(self.selected_phone.id)
                if fresh:
                    self.selected_phone = fresh
                    self.lbl_prod_name.configure(text=fresh.nombre)
                    self.lbl_stock_status.configure(text=f"Disponible: {fresh.stock}")
                else:
                    # The product was removed; reset selection
                    self.reset_selection()
            except Exception:
                # On any error, ensure UI consistency but don't crash
                self.reset_selection()

        # Ensure UI updates are processed
        try:
            self.catalog_scroll.update_idletasks()
        except Exception:
            pass

    def _populate_catalog(self):
        # Clear
        for w in self.catalog_scroll.winfo_children():
            w.destroy()

        phones = self.s_inv.obtener_todos_telefonos()

        # Grid layout for cards (e.g. 3 columns)
        cols = 3
        for i, phone in enumerate(phones):
            if phone.stock <= 0:
                continue

            row = i // cols
            col = i % cols

            self._create_product_card(phone, row, col)

    def _create_product_card(self, phone, r, c):
        frame = ctk.CTkFrame(self.catalog_scroll, width=180, height=220, fg_color=("white", "#444444"))
        frame.grid(row=r, column=c, padx=10, pady=10)

        # Make whole frame clickable
        frame.bind("<Button-1>", lambda e, p=phone: self.select_product(p))

        # Image
        if phone.ruta_imagen and os.path.exists(phone.ruta_imagen):
            try:
                pil_img = Image.open(phone.ruta_imagen)
                pil_img.thumbnail((120, 120))
                img = ctk.CTkImage(pil_img, size=(100, 100))
                lbl_img = ctk.CTkLabel(frame, text="", image=img)
                lbl_img.pack(pady=10)
                lbl_img.bind("<Button-1>", lambda e, p=phone: self.select_product(p))
            except Exception:
                ctk.CTkLabel(frame, text="[No IMG]").pack(pady=40)
        else:
            ctk.CTkLabel(frame, text="[No IMG]").pack(pady=40)

        # Labels
        lbl_name = ctk.CTkLabel(frame, text=phone.nombre, font=("Arial", 12, "bold"), wraplength=160)
        lbl_name.pack()
        lbl_name.bind("<Button-1>", lambda e, p=phone: self.select_product(p))

        lbl_price = ctk.CTkLabel(frame, text=f"Base: ${phone.costo_original_usd}", text_color="gray")
        lbl_price.pack()
        lbl_price.bind("<Button-1>", lambda e, p=phone: self.select_product(p))

        stk_color = "#2ec4b6" if phone.stock > 5 else ("#ff9f1c" if phone.stock > 2 else "#e63946")
        lbl_stock = ctk.CTkLabel(frame, text=f"Stock: {phone.stock}", text_color=stk_color, font=("Arial", 11, "bold"))
        lbl_stock.pack(side="bottom", pady=5)
        lbl_stock.bind("<Button-1>", lambda e, p=phone: self.select_product(p))

    def select_product(self, phone):
        self.selected_phone = phone
        self.lbl_prod_name.configure(text=phone.nombre)
        self.lbl_stock_status.configure(text=f"Disponible: {phone.stock}")
        self.check_ready()
        self.update_calculations()

    def on_client_select(self, name):
        if name in self.customers_map:
            self.selected_client_id = self.customers_map[name]
            self.check_ready()

    def check_ready(self):
        if self.selected_phone and self.selected_client_id:
            self.btn_process.configure(state="normal", fg_color=AppColors.PRIMARY)
        else:
            self.btn_process.configure(state="disabled", fg_color="gray")

    def reset_selection(self):
        self.selected_phone = None
        self.lbl_prod_name.configure(text="Ninguno")
        self.lbl_stock_status.configure(text="--")
        self.entry_initial.delete(0, "end")
        self.lbl_total_usd.configure(text="$0.00")
        self.lbl_total_bs.configure(text="Bs 0.00")
        self.lbl_installment_val.configure(text="Cuota: $0.00")
        self.lbl_balance_val.configure(text="Saldo: $0.00")
        self.check_ready()

    def update_calculations(self, *args):
        if not self.selected_phone:
            return

        try:
            margen = float(self.margen_var.get())
            tasa = float(self.tasa_var.get())

            # Use centralized logic from Service!
            final_usd = self.s_ventas.calcular_precio_con_margen(self.selected_phone.costo_original_usd, margen)

            # Initial Pay
            try:
                initial_val = self.entry_initial.get()
                initial = float(initial_val) if initial_val else 0.0
            except Exception:
                initial = 0.0

            # Installments
            cuotas_str = self.combo_installments.get()
            cuotas = 0 if "Contado" in cuotas_str else int(cuotas_str)

            # Centralized Calculation (Using existing Service logic)
            res = self.s_ventas.calcular_totales_venta(final_usd, initial, cuotas, tasa)

            # UI Update
            self.lbl_total_usd.configure(text=f"${res.precio_final_usd:.2f}")
            self.lbl_total_bs.configure(text=f"Bs {res.precio_final_bs:.2f}")

            if res.es_contado:
                self.lbl_installment_val.configure(text="CONTADO")
                self.lbl_balance_val.configure(text="Sin Deuda")
            else:
                self.lbl_installment_val.configure(text=f"Cuota ({cuotas}): ${res.monto_cuota_usd:.2f}")
                self.lbl_balance_val.configure(text=f"A Financiar: ${res.saldo_pendiente_usd:.2f}")

        except (ValueError, BusinessRuleError):
            # Si hay error en cálculo (input invalido o regla negocio), no actualizamos o limpiamos
            pass

    def process_sale(self):
        if not self.selected_phone or not self.selected_client_id:
            messagebox.showwarning("Faltan Datos", "Seleccione Cliente y Producto")
            return

        # Get final values for execution
        try:
            margen = float(self.margen_var.get())
            tasa = float(self.tasa_var.get())

            # Use Service!
            final_usd = self.s_ventas.calcular_precio_con_margen(self.selected_phone.costo_original_usd, margen)

            try:
                initial = float(self.entry_initial.get())
            except Exception:
                initial = 0.0

            cuotas_str = self.combo_installments.get()
            cuotas = 0 if "Contado" in cuotas_str else int(cuotas_str)

            # Execution
            self.s_ventas.procesar_venta(
                self.selected_client_id, self.selected_phone.id, final_usd, initial, cuotas, tasa
            )

            messagebox.showinfo("Éxito", "Venta Registrada Correctamente")
            self.reset_selection()
            self.load_data()  # Refresh catalog stock

        except BusinessRuleError as e:
            messagebox.showwarning("Regla de Negocio", f"{e}")
        except InventoryError as e:
            messagebox.showerror("Error de Inventario", f"{e}")
        except SmartCreditError as e:
            messagebox.showerror("Error", f"{e}")
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado: {e}")
