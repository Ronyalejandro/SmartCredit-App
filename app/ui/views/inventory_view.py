import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from app.services.inventory_service import ServiceInventario
from app.ui.styles import AppColors
from app.ui.components.toast import ToastNotification
import os


class InventoryView(ctk.CTkFrame):
    def __init__(self, master, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.service = ServiceInventario()
        self.image_path_var = ctk.StringVar()
        # Optional callback to notify other views about inventory changes
        self.on_change = on_change

        self._init_ui()
        self.refresh_list()

    def _init_ui(self):
        # Layout: Left side (List), Right side (Form)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Left Side: Inventory List ---
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Lista de Teléfonos")
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Right Side: Form ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.form_frame, text="Agregar / Editar Teléfono", font=("Arial", 16, "bold")).pack(pady=10)

        # Fields
        self.entry_nombre = self._create_input("Nombre / Modelo")
        self.entry_costo = self._create_input("Costo Original (USD)")
        self.entry_stock = self._create_input("Stock Inicial")

        # Image Selection
        ctk.CTkLabel(self.form_frame, text="Imagen").pack(pady=(10, 0))
        self.btn_image = ctk.CTkButton(self.form_frame, text="Seleccionar Imagen", command=self.select_image)
        self.btn_image.pack(pady=5)
        self.lbl_image_path = ctk.CTkLabel(
            self.form_frame, textvariable=self.image_path_var, text_color="gray", font=("Arial", 10)
        )
        self.lbl_image_path.pack()

        # Action Buttons
        button_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        button_container.pack(pady=20, fill="x")

        ctk.CTkButton(button_container, text="Guardar", command=self.save_phone, fg_color=AppColors.PRIMARY).pack(
            fill="x", pady=5
        )
        ctk.CTkButton(button_container, text="Limpiar", command=self.clear_form, fg_color="gray").pack(fill="x", pady=5)

    def _create_input(self, label):
        ctk.CTkLabel(self.form_frame, text=label).pack(pady=(10, 0))
        entry = ctk.CTkEntry(self.form_frame)
        entry.pack(pady=5)
        return entry

    def select_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png;*.jpeg")])
        if filename:
            self.image_path_var.set(filename)

    def save_phone(self):
        nombre = self.entry_nombre.get()
        costo = self.entry_costo.get()
        stock = self.entry_stock.get()
        rut_img = self.image_path_var.get()

        if not nombre or not costo or not stock:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            costo_val = float(costo)
            stock_val = int(stock)
            self.service.agregar_telefono(nombre, costo_val, stock_val, rut_img)
            self.refresh_list()
            # Notify other views (e.g., POS) that inventory changed
            try:
                if callable(self.on_change):
                    self.on_change()
            except Exception:
                pass
            self.clear_form()
            messagebox.showinfo("Éxito", "Teléfono registrado correctamente")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.entry_nombre.delete(0, "end")
        self.entry_costo.delete(0, "end")
        self.entry_stock.delete(0, "end")
        self.image_path_var.set("")

    def refresh_list(self):
        # Clear existing items
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        phones = self.service.obtener_todos_telefonos()

        for p in phones:
            self._create_phone_card(p)

        # Force UI update
        self.list_frame.update_idletasks()

    def _create_phone_card(self, phone):
        # Determine Color based on Stock
        if phone.stock == 0:
            bg_color = (AppColors.DANGER, "#990000")  # Rojo fuerte
            status_text = "AGOTADO"
        elif phone.stock < 5:
            bg_color = (AppColors.WARNING, "#cc7a00")  # Amarillo/Naranja
            status_text = "STOCK BAJO"
        else:
            bg_color = ("gray85", "gray25")
            status_text = ""

        card = ctk.CTkFrame(self.list_frame, fg_color=bg_color)
        card.pack(fill="x", pady=5, padx=5)

        # Image Thumbnail
        if phone.ruta_imagen and os.path.exists(phone.ruta_imagen):
            try:
                pil_img = Image.open(phone.ruta_imagen)
                pil_img.thumbnail((50, 50))
                img = ctk.CTkImage(light_image=pil_img, size=(50, 50))
                lbl_img = ctk.CTkLabel(card, text="", image=img)
                lbl_img.pack(side="left", padx=5)
            except Exception:
                pass

        # Info
        info_text = f"{phone.nombre}\nStock: {phone.stock} {status_text} | Costo: ${phone.costo_original_usd}"
        ctk.CTkLabel(card, text=info_text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)

        # Quick Update Button (visible if stock < 5 or convenient always? Proposal implies contextual)
        if phone.stock < 10:  # Umbral generoso para falicitar gestión
            ctk.CTkButton(
                card,
                text="+",
                width=30,
                height=24,
                fg_color=AppColors.SUCCESS,
                command=lambda p_id=phone.id, p_name=phone.nombre: self.prompt_quick_update(p_id, p_name),
            ).pack(side="right", padx=2)

        # Delete Button
        ctk.CTkButton(
            card, text="X", width=30, fg_color=AppColors.DANGER, command=lambda p_id=phone.id: self.delete_phone(p_id)
        ).pack(side="right", padx=5)

    def delete_phone(self, phone_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar este teléfono?"):
            self.service.eliminar_telefono(phone_id)
            self.refresh_list()
            try:
                if callable(self.on_change):
                    self.on_change()
            except Exception:
                pass

    def prompt_quick_update(self, phone_id, phone_name):
        dialog = ctk.CTkInputDialog(text=f"Agregar Stock para {phone_name}:", title="Actualización Rápida")
        val_str = dialog.get_input()

        if val_str:
            try:
                val = int(val_str)
                if val <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser positiva")
                    return

                self.service.actualizar_stock_rapido(phone_id, val)
                self.refresh_list()

                # Notify other views
                try:
                    if callable(self.on_change):
                        self.on_change()
                except Exception:
                    pass

                # Toast Notification (Professional UX)
                ToastNotification(self, "Actualizado", f"Se agregaron {val} unidades.", color="green")

            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido.")
