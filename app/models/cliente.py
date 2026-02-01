class Cliente:
    def __init__(self, id, nombre, cedula, telefono):
        self.id = id
        self.nombre = nombre
        self.cedula = cedula
        self.telefono = telefono

    @staticmethod
    def from_row(row):
        return Cliente(*row)
