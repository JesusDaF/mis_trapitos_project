import sys
import os

# Ajuste de ruta para importar desde 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mis_trapitos.database_conexion.db_manager import DBManager
from mis_trapitos.database_conexion.queries import VentasQueries

def asegurarRequisitosPrevios(db):
    """
    Crea un empleado dummy y busca la variante creada en el test anterior
    para asegurar que la venta pueda realizarse sin errores de FK.
    """
    # 1. Asegurar Empleado (Necesario para la FK id_empleado en Ventas)
    sql_empleado = """
        INSERT INTO Empleados (nombre_completo, usuario, hash_contrasena, rol)
        VALUES ('Empleado Prueba', 'testuser', '12345', 'admin')
        ON CONFLICT (usuario) DO NOTHING
        RETURNING id_empleado
    """
    # Si ya existe, buscamos su ID
    id_empleado = 1 # Valor por defecto si no retorna nada (asumiendo que es el primero)
    res_emp = db.ejecutarInsertReturning(sql_empleado)
    
    if res_emp:
        id_empleado = res_emp[0]
    else:
        # Si no devolvió nada es porque ya existía, lo buscamos
        datos = db.obtenerDatos("SELECT id_empleado FROM Empleados WHERE usuario = 'testuser'")
        if datos:
            id_empleado = datos[0][0]

    # 2. Buscar ID de la variante "Camiseta Running Pro" - Talla M - Rojo
    # (Datos creados en test_data_load.py)
    sql_variante = """
        SELECT v.id_variante, v.stock_disponible 
        FROM Variantes_Producto v
        JOIN Productos p ON v.id_producto = p.id_producto
        WHERE p.descripcion LIKE '%Running Pro%' AND v.talla = 'M' AND v.color = 'Rojo'
    """
    res_var = db.obtenerDatos(sql_variante)
    
    if not res_var:
        print("Error: No se encontraron los datos de prueba (Camiseta Running Pro). Ejecuta test_data_load.py primero.")
        return None, None, None

    return id_empleado, res_var[0][0], res_var[0][1] # id_empleado, id_variante, stock_inicial

def ejecutarPruebaVenta():
    """
    Simula una transacción completa de venta:
    1. Abre conexión manual.
    2. Crea Venta -> Registra Detalle -> Descuenta Stock.
    3. Hace COMMIT si todo es correcto o ROLLBACK si falla.
    """
    db = DBManager()
    ventas_queries = VentasQueries()

    print("---Iniciando Simulación de Venta Transaccional ---")

    # --- PASO 0: Preparación de Datos ---
    id_empleado, id_variante, stock_inicial = asegurarRequisitosPrevios(db)
    
    if not id_variante:
        return

    cantidad_a_vender = 2 # cantidad de camisetas a vender
    precio_venta = 250.00 # precio unitario
    total_venta = cantidad_a_vender * precio_venta # total calculado
    
    print(f"Estado Inicial -> Producto ID: {id_variante} | Stock: {stock_inicial} | Intentando vender: {cantidad_a_vender}")

    # --- INICIO DE LA TRANSACCIÓN ---
    conexion_activa = db.obtenerConexion() # abrimos conexión manual
    
    try:
        if conexion_activa:
            print("\nTransacción iniciada...")

            # 1. Crear el Ticket de Venta
            # Pasamos 'conexion_externa' para que NO haga commit todavía
            id_venta_generada = ventas_queries.crearVenta(
                id_empleado=id_empleado,
                metodo_pago='efectivo',
                total=total_venta,
                conexion_externa=conexion_activa
            )
            print(f"   -> Paso 1: Ticket de Venta creado con ID: {id_venta_generada}")

            if not id_venta_generada:
                raise Exception("Fallo al crear el ticket de venta")

            # 2. Registrar el Detalle (Productos)
            ventas_queries.registrarDetalleVenta(
                id_venta=id_venta_generada,
                id_variante=id_variante,
                cantidad=cantidad_a_vender,
                precio_unitario=precio_venta,
                conexion_externa=conexion_activa
            )
            print(f"   -> Paso 2: Detalles registrados (2 camisetas)")

            # 3. Descontar Inventario
            stock_descontado = ventas_queries.descontarStock(
                id_variante=id_variante,
                cantidad_vendida=cantidad_a_vender,
                conexion_externa=conexion_activa
            )
            
            if not stock_descontado:
                raise Exception("Fallo al descontar el stock (posiblemente id incorrecto)")
            
            print(f"   -> Paso 3: Stock descontado en memoria")

            # --- MOMENTO DE LA VERDAD ---
            # Si llegamos aquí sin errores, guardamos todo.
            conexion_activa.commit()
            print("\n¡ÉXITO! Transacción confirmada (COMMIT realizado).")

    except Exception as error_transaccion:
        # Si algo falló en cualquiera de los pasos, deshacemos TODO.
        if conexion_activa:
            conexion_activa.rollback()
        print(f"\nERROR CRÍTICO: {error_transaccion}")
        print("↩Se ha realizado un ROLLBACK. Ningún dato fue alterado.")

    finally:
        # Siempre cerramos la conexión manual al terminar
        db.cerrarConexion(conexion_activa)

    # --- VERIFICACIÓN FINAL ---
    print("\n--- Verificación de Integridad ---")
    # Consultamos el stock final (ya sin transacción, lectura normal)
    stock_final_data = db.obtenerDatos(f"SELECT stock_disponible FROM Variantes_Producto WHERE id_variante = {id_variante}")
    stock_final = stock_final_data[0][0]
    
    print(f"Stock Antes: {stock_inicial}")
    print(f"Stock Ahora: {stock_final}")
    
    if stock_final == (stock_inicial - cantidad_a_vender):
        print("Resultado Correcto: El inventario se actualizó perfectamente.")
    else:
        print("Advertencia: El stock no coincide con lo esperado.")

if __name__ == "__main__":
    ejecutarPruebaVenta()