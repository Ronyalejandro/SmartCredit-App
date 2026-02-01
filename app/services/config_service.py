import json
import os


class ConfigService:
    _instance = None
    CONFIG_FILE = "config.json"

    DEFAULT_CONFIG = {"tasa_cambio": "40.0", "margen_ganancia": "65"}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        self.config = self.DEFAULT_CONFIG.copy()
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")  # We'll replace this with logger later

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_tasa(self):
        return self.config.get("tasa_cambio", "40.0")

    def set_tasa(self, tasa: str):
        self.config["tasa_cambio"] = tasa
        self.save_config()

    def get_margen(self):
        return self.config.get("margen_ganancia", "65")

    def set_margen(self, margen: str):
        self.config["margen_ganancia"] = margen
        self.save_config()
