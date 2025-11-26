import sys
import os

# Ajuste de ruta para importar desde 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mis_trapitos.logica.ventas_control import SalesController
from mis_trapitos.database_conexion.queries import InventarioQueries, UsuariosQueries

def obtenerDatosPrueba():
    """
    Ayudante para encontrar un empleado y un producto con stock 
    para realizar la prueba.
    """
    inv_queries = InventarioQueries()
    user_queries = UsuariosQueries()

    # 1. Buscar Empleado (Admin creado en tests anteriores)
    datos_usuario = user_queries.obtenerUsuarioPorUser('testuser')
    id_empleado = datos_usuario[0] if datos_usuario else None

    # 2. Buscar un producto con stock > 0
    inventario = inv_queries.obtenerProductosEnInventario()
    # inventario devuelve tuplas: (descripcion, talla, color, stock, precio)
    # Necesitamos el ID de la variante. Como obtenerProductosEnInventario 
    # es para "vista", haremos una consulta rápida directa para obtener el ID correcto.
    
    #Usamos DBManager directo para buscar un ID válido rápidamente
    sql_buscar_id = """
        SELECT v.id_variante, v.stock_disponible, p.precio_base 
        FROM Variantes_Producto v
        JOIN Productos p ON v.id_producto = p.id_producto
        WHERE v.stock_disponible > 0
        LIMIT 1
    """
    res = inv_queries.db.obtenerDatos(sql_buscar_id)
    
    datos_producto = None
    if res:
        datos_producto = {
            'id': res[0][0],
            'stock': res[0][1],
            'precio': res[0][2]
        }

    return id_empleado, datos_producto

def ejecutarTestControlador():
    """
    Ejecuta dos pruebas clave:
    1. Venta Exitosa (debe bajar stock).
    2. Venta Fallida por Stock Insuficiente (no debe cambiar nada).
    """
    controller = SalesController()
    
    print("--- TEST DE CONTROLADOR DE VENTAS ---")

    # --- PREPARACIÓN ---
    id_empleado, prod_data = obtenerDatosPrueba()

    if not id_empleado:
        print("Error: No se encontró el usuario 'testuser'. Ejecuta test_sale_transaction.py primero para crearlo.")
        return
    if not prod_data:
        print("Error: No hay productos con stock en la BD. Ejecuta test_data_load.py.")
        return

    print(f"Empleado ID: {id_empleado}")
    print(f"Producto ID: {prod_data['id']} | Stock Inicial: {prod_data['stock']} | Precio: ${prod_data['precio']}")

    # ==========================================
    # CASO 1: VENTA EXITOSA
    # ==========================================
    print("\nCASO 1: Intentando venta válida (1 unidad)...")
    
    carrito_valido = [{
        'id_variante': prod_data['id'],
        'cantidad': 1,
        'precio': prod_data['precio'],
        'descuento': 0
    }]

    exito, mensaje = controller.procesarVentaNueva(
        id_empleado=id_empleado,
        id_cliente=None, # Cliente anónimo
        metodo_pago='efectivo',
        carrito_compras=carrito_valido
    )

    if exito:
        print(f"   Resultado: {mensaje}")
    else:
        print(f"   Falló inesperadamente: {mensaje}")

    # ==========================================
    # CASO 2: VENTA FALLIDA (STOCK INSUFICIENTE)
    # ==========================================
    print("\n CASO 2: Intentando vender más del stock disponible...")
    
    # Consultamos stock actual (debería ser inicial - 1)
    # Lo forzamos a fallar pidiendo 1000 unidades
    carrito_excesivo = [{
        'id_variante': prod_data['id'],
        'cantidad': 1000, 
        'precio': prod_data['precio']
    }]

    exito_fail, mensaje_fail = controller.procesarVentaNueva(
        id_empleado=id_empleado,
        id_cliente=None,
        metodo_pago='tarjeta',
        carrito_compras=carrito_excesivo
    )

    if not exito_fail:
        print(f"   Comportamiento Correcto (Venta rechazada).")
        print(f"      Mensaje del sistema: '{mensaje_fail}'")
    else:
        print(f"   ERROR GRAVE: El sistema permitió vender sin stock.")

    print("\n--- Fin del Test ---")

if __name__ == "__main__":
    ejecutarTestControlador()