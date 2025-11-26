from mis_trapitos.database_conexion.queries import VentasQueries, InventarioQueries, DescuentosQueries
from mis_trapitos.core.logger import log

class SalesController:
    """
    Controlador encargado de la lógica de negocio para las ventas.
    Coordina la creación del ticket, el registro de productos y la actualización de inventario
    en una única transacción atómica.
    """

    def __init__(self):
        """Inicializa las consultas de ventas"""
        self.ventas_queries = VentasQueries()

    def calcularTotal(self, carrito_compras):
        """
        Calcula el monto total de la venta basado en el carrito.
        carrito_compras: Lista de diccionarios [{'id_variante': 1, 'precio': 100, 'cantidad': 2}, ...]
        """
        total_calculado = 0.0
        for item in carrito_compras:
            subtotal = float(item['precio']) * int(item['cantidad'])
            total_calculado += subtotal
        return total_calculado

    def procesarVentaNueva(self, id_empleado, id_cliente, metodo_pago, carrito_compras):
        """
        Ejecuta la venta aplicando lógica de DESCUENTOS AUTOMÁTICOS y MANUALES.
        """
        desc_queries = DescuentosQueries()
        inv_queries = InventarioQueries() # Para verificar precios reales si fuera necesario

        # --- VALIDACIONES PREVIAS ---
        if not carrito_compras:
            log.warning(f"Intento de venta con carrito vacío. Empleado: {id_empleado}")
            return False, "Carrito vacío."
        if not id_empleado:
            return False, "Empleado no identificado."

        # --- INICIO DE TRANSACCIÓN ---
        conn = self.ventas_queries.db.obtenerConexion()
        if not conn: 
            log.critical("Fallo al obtener conexión de BD para venta.")
            return False, "Error de BD"

        try:
            total_venta_acumulado = 0.0
            detalles_para_insertar = [] # Guardamos datos procesados para insertar después
            
            # --- CÁLCULO Y VALIDACIÓN DE PRECIOS ---
            # Antes de crear el ticket, procesamos cada producto para calcular su precio final real
            
            for item in carrito_compras:
                id_variante = item['id_variante']
                cantidad = int(item['cantidad'])
                precio_base = float(item['precio']) # Precio original del producto
                descuento_manual = float(item.get('descuento_manual', 0)) # % Manual ingresado por usuario

                if cantidad <= 0: continue

                # 1. Buscar Descuento Automático (Vigente en BD)
                # Pasamos 'conn' para que la consulta sea rápida dentro de la misma sesión 
                porc_auto = desc_queries.obtenerDescuentoActivo(id_variante, conexion_externa=conn)
                
                
                porcentaje_final = 0.0
                tipo_descuento = "Ninguno"

                if descuento_manual > 0:
                    porcentaje_final = descuento_manual
                    tipo_descuento = "Manual"
                elif porc_auto > 0:
                    porcentaje_final = porc_auto
                    tipo_descuento = "Automático"

                # Validacion de seguridad: No permitir descuentos > 100% o negativos
                if porcentaje_final < 0 or porcentaje_final > 100:
                    raise Exception(f"Descuento inválido ({porcentaje_final}%) en producto {id_variante}")

                # 2. Calcular Precio Final Unitario
                monto_descuento = precio_base * (porcentaje_final / 100)
                precio_final_unitario = precio_base - monto_descuento
                
                subtotal_linea = precio_final_unitario * cantidad
                total_venta_acumulado += subtotal_linea

                # Guardamos los datos listos para no recalcular abajo
                detalles_para_insertar.append({
                    'id_variante': id_variante,
                    'cantidad': cantidad,
                    'precio_grabado': precio_final_unitario, # Precio ya con descuento
                    'descuento_grabado': monto_descuento # Dinero descontado por unidad
                })

            # --- INSERCIÓN EN BD ---
            
            log.info(f"Iniciando venta. Empleado: {id_empleado}, Total calc: {total_venta_acumulado}")

            # 1. Crear Ticket
            id_venta = self.ventas_queries.crearVenta(
                id_empleado, metodo_pago, total_venta_acumulado, id_cliente, conexion_externa=conn
            )
            
            if not id_venta: raise Exception("Error al crear ticket.")

            # 2. Insertar Detalles y Descontar Stock
            for det in detalles_para_insertar:
                self.ventas_queries.registrarDetalleVenta(
                    id_venta,
                    det['id_variante'],
                    det['cantidad'],
                    det['precio_grabado'], # Guardamos el precio al que FINALMENTE se vendió
                    det['descuento_grabado'],
                    conexion_externa=conn
                )

                exito_stock = self.ventas_queries.descontarStock(
                    det['id_variante'], det['cantidad'], conexion_externa=conn
                )
                if not exito_stock:
                    raise Exception(f"Stock insuficiente para variante {det['id_variante']}")

            conn.commit()
            log.info(f"Venta finalizada exitosamente. ID: {id_venta}")
            return True, f"Venta registrada. Total: ${total_venta_acumulado:.2f}"

        except Exception as e:
            # D. REVERSIÓN (ROLLBACK)
            conn.rollback()
            mensaje_error = str(e)
            
            # Registramos el error técnico en el log
            log.error(f"Transacción de venta fallida: {mensaje_error}")

            # Retornamos un mensaje amigable al usuario según el tipo de error
            if "check constraint" in mensaje_error.lower() or "stock_disponible" in mensaje_error.lower():
                return False, "Error: Stock insuficiente para completar la venta."
            
            return False, f"Ocurrió un error al procesar la venta: {mensaje_error}"
            
        finally:
            self.ventas_queries.db.cerrarConexion(conn)