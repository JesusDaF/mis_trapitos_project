## Consultas a la base de datos

from mis_trapitos.database_conexion.db_manager import DBManager
from mis_trapitos.core.logger import log

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
        """
        Obtiene inventario incluyendo el ID.
        CAMBIO: Solo trae productos donde activo = TRUE.
        """
        sql_inventario = """
            SELECT v.id_variante, p.id_producto, p.descripcion, v.talla, v.color, v.stock_disponible, p.precio_base
            FROM Variantes_Producto v
            JOIN Productos p ON v.id_producto = p.id_producto
            WHERE p.activo = TRUE 
            ORDER BY p.id_producto DESC
        """
        return self.db.obtenerDatos(sql_inventario, conexion_externa=conexion_externa)
    
    def actualizarStock(self, id_variante, nuevo_stock, conexion_externa=None):
        """Sobrescribe el stock de una variante específica."""
        sql = "UPDATE Variantes_Producto SET stock_disponible = %s WHERE id_variante = %s"
        return self.db.ejecutarConsulta(sql, (nuevo_stock, id_variante), conexion_externa)

    def actualizarPrecioProducto(self, id_producto, nuevo_precio, conexion_externa=None):
        """Actualiza el precio base del producto padre."""
        sql = "UPDATE Productos SET precio_base = %s WHERE id_producto = %s"
        return self.db.ejecutarConsulta(sql, (nuevo_precio, id_producto), conexion_externa)
    
    def eliminarProducto(self, id_producto, conexion_externa=None):
        """
        Realiza una BAJA LÓGICA. 
        No borra el registro, solo lo marca como inactivo para ocultarlo.
        """
        sql = "UPDATE Productos SET activo = FALSE WHERE id_producto = %s"
        return self.db.ejecutarConsulta(sql, (id_producto,), conexion_externa)

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
        sql = "SELECT id_cliente, nombre_completo, direccion FROM Clientes WHERE activo = TRUE AND telefono = %s"
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
    def obtenerTodosLosClientes(self, conexion_externa=None):
        """Trae solo clientes activos."""
        sql = "SELECT id_cliente, nombre_completo, telefono, correo_electronico, direccion FROM Clientes WHERE activo = TRUE ORDER BY nombre_completo ASC"
        return self.db.obtenerDatos(sql, conexion_externa=conexion_externa)
    
    def eliminarCliente(self, id_cliente, conexion_externa=None):
        """Baja Lógica: Marca como inactivo."""
        sql = "UPDATE Clientes SET activo = FALSE WHERE id_cliente = %s"
        return self.db.ejecutarConsulta(sql, (id_cliente,), conexion_externa)


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
    """
    Gestiona la seguridad, autenticación y auditoría de los empleados"""
    
    def __init__(self):
        self.db = DBManager()

    def obtenerUsuarioPorUser(self, usuario, conexion_externa=None):
        """
        Busca un empleado activo por su nombre de usuario para el Login.
        Retorna: (id_empleado, nombre, hash_contrasena, rol)
        """
        sql = """
            SELECT id_empleado, nombre_completo, hash_contrasena, rol 
            FROM Empleados 
            WHERE usuario = %s AND activo = TRUE
        """
        # datos_usuario almacena la tupla con la info del empleado encontrado
        datos_usuario = self.db.obtenerDatos(sql, (usuario,), conexion_externa)
        
        return datos_usuario[0] if datos_usuario else None

    def registrarLog(self, id_empleado, accion, descripcion, conexion_externa=None):
        """
        Guarda un registro en la bitácora de movimientos (Auditoría)"""
        sql = """
            INSERT INTO Log_Movimientos (id_empleado, accion, descripcion_detallada)
            VALUES (%s, %s, %s)
        """
        self.db.ejecutarConsulta(
            sql, 
            (id_empleado, accion, descripcion), 
            conexion_externa
        )

    def crearEmpleado(self, nombre, usuario, hash_contrasena, rol='empleado', conexion_externa=None):
        """
        Registra un nuevo empleado en el sistema.
        """
        sql = """
            INSERT INTO Empleados (nombre_completo, usuario, hash_contrasena, rol)
            VALUES (%s, %s, %s, %s) RETURNING id_empleado
        """
        resultado = self.db.ejecutarInsertReturning(
            sql,
            (nombre, usuario, hash_contrasena, rol),
            conexion_externa
        )
        if resultado:
            return resultado[0]
        return None 
    
    def obtenerTodosLosUsuarios(self, conexion_externa=None):
        """Trae solo empleados activos."""
        sql = "SELECT id_empleado, nombre_completo, usuario, rol, activo FROM Empleados WHERE activo = TRUE ORDER BY id_empleado ASC"
        return self.db.obtenerDatos(sql, conexion_externa=conexion_externa)
    
    def eliminarUsuario(self, id_empleado, conexion_externa=None):
        """Baja Lógica."""
        sql = "UPDATE Empleados SET activo = FALSE WHERE id_empleado = %s"
        return self.db.ejecutarConsulta(sql, (id_empleado,), conexion_externa)
    

class ProveedoresQueries:
    """
    Gestiona la información de proveedores y su relación con los productos"""

    def __init__(self):
        self.db = DBManager()

    def registrarProveedor(self, nombre_proveedor, datos_contacto, conexion_externa=None):
        """
        Registra un nuevo proveedor en la base de datos.
        """
        sql = """
            INSERT INTO Proveedores (nombre_proveedor, datos_contacto)
            VALUES (%s, %s) RETURNING id_proveedor
        """
        # id_nuevo_proveedor captura el ID generado tras la inserción
        id_nuevo_proveedor = self.db.ejecutarInsertReturning(
            sql, 
            (nombre_proveedor, datos_contacto), 
            conexion_externa
        )
        
        if id_nuevo_proveedor:
            return id_nuevo_proveedor[0]
        return None

    def obtenerProveedores(self, conexion_externa=None):
        """Trae solo proveedores activos."""
        sql = "SELECT id_proveedor, nombre_proveedor, datos_contacto FROM Proveedores WHERE activo = TRUE"
        return self.db.obtenerDatos(sql, conexion_externa=conexion_externa)

    def asociarProductoProveedor(self, id_proveedor, id_producto, conexion_externa=None):
        """
        Vincula un producto a un proveedor para saber quién lo surte (Reposición).
        """
        sql = """
            INSERT INTO Proveedores_Productos (id_proveedor, id_producto)
            VALUES (%s, %s)
        """
        # filas_afectadas indica si la asociación se guardó correctamente
        filas_afectadas = self.db.ejecutarConsulta(
            sql,
            (id_proveedor, id_producto),
            conexion_externa
        )
        return filas_afectadas > 0

    def obtenerProveedoresDeProducto(self, id_producto, conexion_externa=None):
        """
        Consulta qué proveedores surten un producto específico.
        """
        sql = """
            SELECT p.id_proveedor, p.nombre_proveedor, p.datos_contacto
            FROM Proveedores p
            JOIN Proveedores_Productos pp ON p.id_proveedor = pp.id_proveedor
            WHERE pp.id_producto = %s
        """
        return self.db.obtenerDatos(sql, (id_producto,), conexion_externa)
    
    def eliminarProveedor(self, id_proveedor, conexion_externa=None):
        """Baja Lógica."""
        sql = "UPDATE Proveedores SET activo = FALSE WHERE id_proveedor = %s"
        return self.db.ejecutarConsulta(sql, (id_proveedor,), conexion_externa)
    
class DescuentosQueries:
    """
    Gestiona las ofertas y promociones (RF 1.1).
    """
    def __init__(self):
        self.db = DBManager()

    def registrarDescuento(self, id_producto, porcentaje, fecha_inicio, fecha_fin, conexion_externa=None):
        """
        Crea una nueva regla de descuento para un producto.
        """
        sql = """
            INSERT INTO Descuentos (id_producto, porcentaje, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s) RETURNING id_descuento
        """
        resultado = self.db.ejecutarInsertReturning(
            sql, 
            (id_producto, porcentaje, fecha_inicio, fecha_fin),
            conexion_externa
        )
        return resultado[0] if resultado else None

    def obtenerDescuentoActivo(self, id_variante, conexion_externa=None):
        """
        Busca si existe un descuento VIGENTE para el producto asociado a una variante.
        Retorna el porcentaje (decimal) o None.
        Usa CURRENT_DATE de PostgreSQL para comparar fechas.
        """
        sql = """
            SELECT d.porcentaje 
            FROM Descuentos d
            JOIN Variantes_Producto v ON v.id_producto = d.id_producto
            WHERE v.id_variante = %s 
              AND d.fecha_inicio <= CURRENT_DATE 
              AND d.fecha_fin >= CURRENT_DATE
            ORDER BY d.porcentaje DESC -- Si hay dos ofertas, toma la mayor
            LIMIT 1
        """
        res = self.db.obtenerDatos(sql, (id_variante,), conexion_externa)
        if res:
            return float(res[0][0])
        return 0.0