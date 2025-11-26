from mis_trapitos.database_conexion.db_manager import DBManager

class ReportQueries:
    """
    Clase dedicada exclusivamente a la generación de reportes y estadísticas.
    Corresponde a la sección '3. Consultas a Desarrollar' de los requerimientos.
    """

    def __init__(self):
        self.db = DBManager()

    # 1. ¿Cuál es el producto con más unidades disponibles en inventario?
    def obtenerProductoMayorStock(self):
        sql = """
            SELECT p.descripcion, v.talla, v.color, v.stock_disponible
            FROM Variantes_Producto v
            JOIN Productos p ON v.id_producto = p.id_producto
            ORDER BY v.stock_disponible DESC
            LIMIT 1
        """
        res = self.db.obtenerDatos(sql)
        return res[0] if res else None

    # 2. ¿Qué productos no se han vendido en los últimos tres meses? (O periodo dinámico)
    def obtenerProductosSinVentas(self, dias_atras=90):
        """
        Encuentra productos que no aparecen en ninguna venta reciente.
        """
        sql = """
            SELECT p.descripcion, v.talla, v.color
            FROM Variantes_Producto v
            JOIN Productos p ON v.id_producto = p.id_producto
            WHERE v.id_variante NOT IN (
                SELECT DISTINCT dv.id_variante
                FROM Detalles_Venta dv
                JOIN Ventas ve ON dv.id_venta = ve.id_venta
                WHERE ve.fecha_venta >= CURRENT_DATE - INTERVAL '%s days'
            )
        """
        #Pasamos el intervalo como parámetro seguro
        return self.db.obtenerDatos(sql, (dias_atras,))

    # 3. ¿Cuáles son los métodos de pago más utilizados en los últimos 30 días?
    def obtenerMetodosPagoPopulares(self):
        sql = """
            SELECT metodo_pago, COUNT(*) as cantidad_uso
            FROM Ventas
            WHERE fecha_venta >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY metodo_pago
            ORDER BY cantidad_uso DESC
        """
        return self.db.obtenerDatos(sql)

    # 4. ¿Qué productos han sido comprados en mayor cantidad en el último mes? 
    def obtenerProductosMasVendidosMes(self):
        sql = """
            SELECT p.descripcion, SUM(dv.cantidad) as total_vendido
            FROM Detalles_Venta dv
            JOIN Ventas v ON dv.id_venta = v.id_venta
            JOIN Variantes_Producto vp ON dv.id_variante = vp.id_variante
            JOIN Productos p ON vp.id_producto = p.id_producto
            WHERE v.fecha_venta >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY p.id_producto, p.descripcion
            ORDER BY total_vendido DESC
            LIMIT 5
        """
        return self.db.obtenerDatos(sql)

    # 5. ¿Cuántas ventas se realizaron en los últimos tres días?
    def contarVentasRecientes(self, dias=3):
        sql = """
            SELECT COUNT(*) 
            FROM Ventas 
            WHERE fecha_venta >= CURRENT_DATE - INTERVAL '%s days'
        """
        res = self.db.obtenerDatos(sql, (dias,))
        return res[0][0] if res else 0

    # 6. ¿Qué productos ha comprado un cliente más de una vez?
    def obtenerProductosRecurrentesCliente(self, id_cliente):
        sql = """
            SELECT p.descripcion, COUNT(dv.id_detalle_venta) as veces_comprado
            FROM Detalles_Venta dv
            JOIN Ventas v ON dv.id_venta = v.id_venta
            JOIN Variantes_Producto vp ON dv.id_variante = vp.id_variante
            JOIN Productos p ON vp.id_producto = p.id_producto
            WHERE v.id_cliente = %s
            GROUP BY p.id_producto, p.descripcion
            HAVING COUNT(dv.id_detalle_venta) > 1
        """
        return self.db.obtenerDatos(sql, (id_cliente,))

    # 7. ¿Qué productos tienen un precio superior a un valor y están en stock?
    def buscarProductosCarosEnStock(self, precio_minimo):
        sql = """
            SELECT p.descripcion, p.precio_base, v.stock_disponible
            FROM Variantes_Producto v
            JOIN Productos p ON v.id_producto = p.id_producto
            WHERE p.precio_base > %s AND v.stock_disponible > 0
        """
        return self.db.obtenerDatos(sql, (precio_minimo,))

    # 8. ¿Cuál es el producto que tiene el mayor descuento aplicado actualmente?
    def obtenerProductoMayorDescuento(self):
        sql = """
            SELECT p.descripcion, d.porcentaje
            FROM Descuentos d
            JOIN Productos p ON d.id_producto = p.id_producto
            WHERE d.fecha_inicio <= CURRENT_DATE 
              AND d.fecha_fin >= CURRENT_DATE
            ORDER BY d.porcentaje DESC
            LIMIT 1
        """
        res = self.db.obtenerDatos(sql)
        return res[0] if res else None
