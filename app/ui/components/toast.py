import customtkinter as ctk


class ToastNotification:
    """
    A temporary non-intrusive notification window (Toast).
    """

    def __init__(self, master, title, message, duration=3000, color="green"):
        self.master = master
        self.message = message
        self.duration = duration
        self.color_map = {"green": "#2a9d8f", "red": "#e63946", "blue": "#3a86ff", "orange": "#ff9f1c"}
        self.fg_color = self.color_map.get(color, "gray")

        self.show()

    def show(self):
        # Create Toplevel
        self.top = ctk.CTkToplevel(self.master)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)

        # Position (Bottom Right, simpler than calculating master center for now)
        # Assuming typical screen or relative to master if possible.
        # Using master geometry is tricky without update_idletasks.
        # Let's simple center-bottom or try to guess.

        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        w = 300
        h = 60
        x = ws - w - 20
        y = hs - h - 60

        self.top.geometry(f"{w}x{h}+{x}+{y}")

        # Content
        frame = ctk.CTkFrame(self.top, fg_color=self.fg_color, corner_radius=10)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text=self.message, text_color="white", font=("Arial", 12, "bold")).pack(expand=True)

        # Close Timer
        self.top.after(self.duration, self.destroy)

    def destroy(self):
        try:
            self.top.destroy()
        except Exception:
            pass
