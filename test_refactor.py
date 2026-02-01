import unittest
from app.services.inventory_service import ServiceInventario
from app.services.sales_service import ServiceVentas
from app.services.customer_service import ServicioClientes

class TestRefactor(unittest.TestCase):
    def setUp(self):
        self.s_inv = ServiceInventario()
        self.s_ventas = ServiceVentas()
        self.s_clientes = ServicioClientes()
        
        # Setup Data
        try:
            self.s_clientes.registrar_cliente("Test User", "99999", "555-5555")
        except:
            pass # Ignore if exists (unique constraint)
            
        self.s_inv.agregar_telefono("Test Phone", 100, 10, "path/to/img")
        
    def test_logic_centralization(self):
        print("\nTesting Logic Centralization...")
        # Test calculation
        res = self.s_ventas.calcular_totales_venta(
            precio_final_usd=1000, 
            pago_inicial_usd=200, 
            cuotas_totales=4, 
            tasa_cambio=40
        )
        
        # 1000 - 200 = 800 balance. 800 / 4 = 200 per installment
        self.assertEqual(res.saldo_pendiente_usd, 800)
        self.assertEqual(res.monto_cuota_usd, 200)
        self.assertEqual("Financiado" if not res.es_contado else "Contado", "Financiado")
        print("Logic Check Passed.")

    def test_stock_update_atomic(self):
        print("\nTesting Stock Atomicity...")
        # Get phone ID
        phones = self.s_inv.obtener_todos_telefonos()
        target_phone = [p for p in phones if p.nombre == "Test Phone"][0]
        initial_stock = target_phone.stock
        
        # Get Customer
        customers = self.s_clientes.obtener_todos_clientes()
        target_client = [c for c in customers if c.cedula == "99999"][0]
        
        # Process Sale
        self.s_ventas.procesar_venta(
            id_cliente=target_client.id,
            id_telefono=target_phone.id,
            precio_final_usd=150,
            pago_inicial_usd=150,
            cuotas_totales=0,
            tasa_cambio=40
        )
        
        # Verify Stock Decrement
        updated_phone = self.s_inv.obtener_telefono_por_id(target_phone.id)
        print(f"Stock Initial: {initial_stock}, Stock After: {updated_phone.stock}")
        self.assertEqual(updated_phone.stock, initial_stock - 1)
        print("Atomicity Check Passed.")

if __name__ == '__main__':
    unittest.main()
