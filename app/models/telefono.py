class Telefono:
    def __init__(self, id, nombre, costo_original_usd, stock, ruta_imagen):
        self.id = id
        self.nombre = nombre
        self.costo_original_usd = costo_original_usd
        self.stock = stock
        self.ruta_imagen = ruta_imagen

    @staticmethod
    def from_row(row):
        return Telefono(*row)
