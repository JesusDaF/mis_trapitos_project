from mis_trapitos.database_conexion.db_manager import DBManager

class InventarioQueries:
    """Clase que agrupa las consultas relacionadas con productos y categorías"""

    def __init__(self):
        self.db = DBManager()

    # --- SECCIÓN CATEGORÍAS ---

    def crearCategoria(self, nombre, descripcion, conexion_externa=None):
        """Inserta una nueva categoría. Soporta transacción."""
        sql_insertar = "INSERT INTO Categorias (nombre_categoria, descripcion) VALUES (%s, %s)"
        
        filas_afectadas = self.db.ejecutarConsulta(
            sql_insertar, 
            (nombre, descripcion), 
            conexion_externa
        )
        return filas_afectadas > 0

    def obtenerCategorias(self, conexion_externa=None):
        """Recupera todas las categorías."""
        sql_select = "SELECT id_categoria, nombre_categoria FROM Categorias"
        return self.db.obtenerDatos(sql_select, conexion_externa=conexion_externa)

    # --- SECCIÓN PRODUCTOS ---

    def crearProducto(self, id_categoria, descripcion, precio, conexion_externa=None):
        """Registra un nuevo producto base y retorna ID. Soporta transacción."""
        sql_producto = """
            INSERT INTO Productos (id_categoria, descripcion, precio_base) 
            VALUES (%s, %s, %s) RETURNING id_producto
        """
        resultado = self.db.ejecutarInsertReturning(
            sql_producto, 
            (id_categoria, descripcion, precio), 
            conexion_externa
        )
        
        if resultado:
            return resultado[0]
        return None

    def crearVarianteProducto(self, id_producto, talla, color, stock_inicial, conexion_externa=None):
        """Registra una variante. Soporta transacción."""
        sql_variante = """
            INSERT INTO Variantes_Producto (id_producto, talla, color, stock_disponible)
            VALUES (%s, %s, %s, %s)
        """
        return self.db.ejecutarConsulta(
            sql_variante, 
            (id_producto, talla, color, stock_inicial), 
            conexion_externa
        )

    def obtenerProductosEnInventario(self, conexion_externa=None):
        """Obtiene inventario. Soporta conexión externa (ej. lectura consistente)."""
        sql_inventario = """
            SELECT p.descripcion, v.talla, v.color, v.stock_disponible, p.precio_base
            FROM Variantes_Producto v
            JOIN Productos p ON v.id_producto = p.id_producto
        """
        return self.db.obtenerDatos(sql_inventario, conexion_externa=conexion_externa)

class ClientesQueries:
    """Maneja las operaciones de base de datos relacionadas con los clientes"""

    def __init__(self):
        self.db = DBManager()

    def registrarCliente(self, nombre, direccion, email, telefono, conexion_externa=None):
        """Guarda un nuevo cliente. Soporta transacción."""
        sql = """
            INSERT INTO Clientes (nombre_completo, direccion, correo_electronico, telefono)
            VALUES (%s, %s, %s, %s) RETURNING id_cliente
        """
        resultado = self.db.ejecutarInsertReturning(
            sql, 
            (nombre, direccion, email, telefono), 
            conexion_externa
        )
        if resultado:
            return resultado[0]
        return None

    def buscarClientePorTelefono(self, telefono, conexion_externa=None):
        sql = "SELECT id_cliente, nombre_completo, direccion FROM Clientes WHERE telefono = %s"
        resultado = self.db.obtenerDatos(sql, (telefono,), conexion_externa)
        return resultado[0] if resultado else None
    
    def obtenerHistorialCliente(self, id_cliente, conexion_externa=None):
        sql = """
            SELECT v.fecha_venta, v.monto_total_venta, count(d.id_detalle_venta) as items
            FROM Ventas v
            JOIN Detalles_Venta d ON v.id_venta = d.id_venta
            WHERE v.id_cliente = %s
            GROUP BY v.id_venta
            ORDER BY v.fecha_venta DESC
        """
        return self.db.obtenerDatos(sql, (id_cliente,), conexion_externa)


class VentasQueries:
    """Gestiona el registro de ventas y la actualización de stock asociada"""

    def __init__(self):
        """Inicializa el gestor de base de datos"""
        self.db = DBManager()

    def crearVenta(self, id_empleado, metodo_pago, total, id_cliente=None, conexion_externa=None):
        """
        Crea el encabezado de la venta (Ticket) y retorna su ID.
        Soporta transacción externa.
        """
        sql = """
            INSERT INTO Ventas (id_empleado, id_cliente, metodo_pago, monto_total_venta)
            VALUES (%s, %s, %s, %s) RETURNING id_venta
        """
        # Pasamos la conexion_externa al gestor
        resultado = self.db.ejecutarInsertReturning(
            sql, 
            (id_empleado, id_cliente, metodo_pago, total), 
            conexion_externa
        )
        
        if resultado:
            return resultado[0]
        return None

    def registrarDetalleVenta(self, id_venta, id_variante, cantidad, precio_unitario, descuento=0, conexion_externa=None):
        """
        Registra cada producto individual dentro de una venta.
        Soporta transacción externa.
        """
        sql = """
            INSERT INTO Detalles_Venta (id_venta, id_variante, cantidad, precio_unitario_venta, descuento_aplicado)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.ejecutarConsulta(
            sql, 
            (id_venta, id_variante, cantidad, precio_unitario, descuento), 
            conexion_externa
        )

    def descontarStock(self, id_variante, cantidad_vendida, conexion_externa=None):
        """
        Disminuye el inventario de una variante específica.
        Soporta transacción externa.
        """
        sql = """
            UPDATE Variantes_Producto 
            SET stock_disponible = stock_disponible - %s 
            WHERE id_variante = %s
        """
        filas = self.db.ejecutarConsulta(
            sql, 
            (cantidad_vendida, id_variante), 
            conexion_externa
        )
        return filas > 0

class UsuariosQueries:
    """Maneja la autenticación y auditoría de empleados"""
    
    def __init__(self):
        self.db = DBManager()

    def obtenerUsuarioPorUser(self, usuario, conexion_externa=None):
        """Busca datos de login."""
        sql = "SELECT id_empleado, nombre_completo, hash_contrasena, rol FROM Empleados WHERE usuario = %s AND activo = TRUE"
        resultado = self.db.obtenerDatos(sql, (usuario,), conexion_externa)
        return resultado[0] if resultado else None

    def registrarLog(self, id_empleado, accion, descripcion, conexion_externa=None):
        """Guarda un movimiento en la bitácora. CRÍTICO: Soporta transacción."""
        sql = """
            INSERT INTO Log_Movimientos (id_empleado, accion, descripcion_detallada)
            VALUES (%s, %s, %s)
        """
        self.db.ejecutarConsulta(
            sql, 
            (id_empleado, accion, descripcion), 
            conexion_externa
        )