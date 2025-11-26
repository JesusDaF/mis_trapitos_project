import sys
import os
from datetime import datetime, timedelta

# Ajuste de ruta para importar desde 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mis_trapitos.logica.producto_control import ProductController
from mis_trapitos.logica.ventas_control import SalesController
from mis_trapitos.database_conexion.queries import InventarioQueries, UsuariosQueries

def preparar_escenario():
    """
    Crea un producto de prueba de $100.00 para facilitar los cálculos de porcentaje.
    Retorna: (id_empleado, id_producto, id_variante)
    """
    inv_queries = InventarioQueries()
    usr_queries = UsuariosQueries()
    prod_controller = ProductController()

    print("--- Preparando datos de prueba ---")

    # 1. Obtener Empleado (Admin)
    usuario = usr_queries.obtenerUsuarioPorUser('testuser')
    if not usuario:
        # Si no existe, creamos uno rápido
        id_emp = usr_queries.crearEmpleado("Tester Descuentos", "testuser", "1234", "admin")
    else:
        id_emp = usuario[0]

    # 2. Crear Categoría Test
    cat_nombre = "Test Descuentos"
    lista_cats = inv_queries.obtenerCategorias()
    id_cat = None
    for c in lista_cats:
        if c[1] == cat_nombre:
            id_cat = c[0]
            break
    
    if not id_cat:
        inv_queries.crearCategoria(cat_nombre, "Categoría temporal para pruebas")
        # Buscamos el ID recién creado
        lista_cats = inv_queries.obtenerCategorias()
        id_cat = lista_cats[-1][0]

    # 3. Crear Producto de $100 (Precio base)
    # Usamos el controlador para asegurar la creación atómica
    variantes = [{'talla': 'U', 'color': 'Blanco', 'stock': 100}]
    prod_controller.registrarProductoNuevo(id_cat, "Camisa Base $100", 100.00, variantes)
    
    # 4. Obtener los IDs generados
    # Truco: Buscamos el último producto creado con ese nombre
    sql_buscar = """
        SELECT p.id_producto, v.id_variante 
        FROM Productos p 
        JOIN Variantes_Producto v ON p.id_producto = v.id_producto
        WHERE p.descripcion = 'Camisa Base $100'
        ORDER BY p.id_producto DESC LIMIT 1
    """
    res = inv_queries.db.obtenerDatos(sql_buscar)
    
    return id_emp, res[0][0], res[0][1]

def ejecutar_pruebas_descuento():
    prod_controller = ProductController()
    sales_controller = SalesController()

    try:
        id_empleado, id_producto, id_variante = preparar_escenario()
    except Exception as e:
        print(f"Error al preparar datos: {e}")
        return

    print(f"\nDatos: Producto ID {id_producto} | Variante ID {id_variante} | Precio Base: $100.00")

    # ==============================================================================
    # PRUEBA 1: CONFIGURAR OFERTA AUTOMÁTICA (20%)
    # ==============================================================================
    print("\n🔹 PRUEBA 1: Configurar Oferta Automática del 20%")
    
    hoy = datetime.now().strftime('%Y-%m-%d')
    manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    exito_oferta, msg_oferta = prod_controller.agregarOferta(id_producto, 20, hoy, manana)
    
    if exito_oferta:
        print(f"  Oferta creada: {msg_oferta}")
    else:
        print(f"  Falló al crear oferta: {msg_oferta}")
        return

    # ==============================================================================
    # PRUEBA 2: VENTA CON DESCUENTO AUTOMÁTICO
    # ==============================================================================
    print("\n🔹 PRUEBA 2: Venta normal (Debe aplicar el 20% auto)")
    print("   Expectativa: Precio $100 - 20% = $80.00 Total")

    carrito_auto = [{
        'id_variante': id_variante,
        'cantidad': 1,
        'precio': 100.00,
        'descuento_manual': 0 # Sin descuento manual
    }]

    exito_v1, msg_v1 = sales_controller.procesarVentaNueva(
        id_empleado, None, 'efectivo', carrito_auto
    )

    if exito_v1 and "80.00" in msg_v1:
        print(f"   ÉXITO: El sistema cobró $80.00. (Mensaje: {msg_v1})")
    else:
        print(f"   FALLO: El cobro fue incorrecto. (Mensaje: {msg_v1})")

    # ==============================================================================
    # PRUEBA 3: VENTA CON DESCUENTO MANUAL (PRIORIDAD)
    # ==============================================================================
    print("\n PRUEBA 3: Venta con Descuento Manual del 50%")
    print("   Escenario: El producto tiene 20% Auto, pero el vendedor ingresa 50% Manual.")
    print("   Expectativa: Manual (50%) mata a Automático (20%). Total esperado: $50.00")

    carrito_manual = [{
        'id_variante': id_variante,
        'cantidad': 1,
        'precio': 100.00,
        'descuento_manual': 50 # <-- Forzamos 50%
    }]

    exito_v2, msg_v2 = sales_controller.procesarVentaNueva(
        id_empleado, None, 'efectivo', carrito_manual
    )

    if exito_v2 and "50.00" in msg_v2:
        print(f"    ÉXITO: El sistema respetó el manual y cobró $50.00. (Mensaje: {msg_v2})")
    elif exito_v2 and "80.00" in msg_v2:
        print(f"    FALLO: El sistema ignoró el manual y usó el automático.")
    else:
        print(f"    FALLO: Resultado inesperado. (Mensaje: {msg_v2})")

    print("\n---  Fin de las pruebas de descuento ---")

if __name__ == "__main__":
    ejecutar_pruebas_descuento()