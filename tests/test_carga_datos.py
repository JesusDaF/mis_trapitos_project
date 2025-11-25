import sys
import os

# Ajuste de ruta para importar desde 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mis_trapitos.database_conexion.queries import InventarioQueries

def ejecutarPruebaCarga():
    """
    Script de prueba de integración:
    1. Crea una categoría.
    2. Crea un producto asociado a esa categoría.
    3. Crea variantes (talla/color) para ese producto.
    4. Muestra el inventario final.
    """
    gestor = InventarioQueries()
    
    print("---Iniciando Prueba de Carga de Datos ---")

    # --- PASO 1: Crear Categoría ---
    nombre_cat_prueba = "Ropa Deportiva"
    
    print(f"1. Intentando crear categoría: '{nombre_cat_prueba}'...")
    exito_cat = gestor.crearCategoria(nombre_cat_prueba, "Ropa para gimnasio y correr")
    
    if exito_cat:
        print(" Categoría creada (o ya existía).")
    else:
        print(" No se pudo crear la categoría (quizás ya existe).")

    # --- PASO 2: Obtener ID de la Categoría ---
    # Necesitamos el ID para poder crear el producto. Buscamos en la lista de categorías.
    lista_categorias = gestor.obtenerCategorias()
    id_categoria_seleccionada = None

    for cat in lista_categorias:
        # cat es una tupla: (id_categoria, nombre_categoria)
        if cat[1] == nombre_cat_prueba:
            id_categoria_seleccionada = cat[0]
            break
    
    if id_categoria_seleccionada:
        print(f"  ID de categoría '{nombre_cat_prueba}' encontrado: {id_categoria_seleccionada}")

        # --- PASO 3: Crear Producto Base ---
        print("\n2. Creando producto base...")
        nombre_prod = "Camiseta Running Pro"
        precio_prod = 250.00
        
        # Guardamos el ID del nuevo producto que nos devuelve la función
        id_nuevo_producto = gestor.crearProducto(id_categoria_seleccionada, nombre_prod, precio_prod)

        if id_nuevo_producto:
            print(f"  Producto '{nombre_prod}' creado con ID: {id_nuevo_producto}")

            # --- PASO 4: Crear Variantes ---
            print("\n3. Agregando inventario (Variantes)...")
            
            # Variante 1: Talla M, Rojo
            gestor.crearVarianteProducto(id_nuevo_producto, "M", "Rojo", 10)
            print("   -> Agregado: Talla M / Rojo (10 u.)")
            
            # Variante 2: Talla L, Negro
            gestor.crearVarianteProducto(id_nuevo_producto, "L", "Negro", 5)
            print("   -> Agregado: Talla L / Negro (5 u.)")

        else:
            print("  Error: No se pudo crear el producto.")
    else:
        print("  Error: No se encontró la categoría necesaria para continuar.")

    # --- PASO 5: Verificación Final ---
    print("\n--- Verificando Inventario en Base de Datos ---")
    inventario_actual = gestor.obtenerProductosEnInventario()
    
    if inventario_actual:
        print(f"{'PRODUCTO':<25} | {'TALLA':<6} | {'COLOR':<10} | {'STOCK':<5} | {'PRECIO'}")
        print("-" * 65)
        for item in inventario_actual:
            # item = (descripcion, talla, color, stock, precio)
            print(f"{item[0]:<25} | {item[1]:<6} | {item[2]:<10} | {item[3]:<5} | ${item[4]}")
    else:
        print("El inventario está vacío.")

    print("\n--- Fin de la prueba ---")

if __name__ == "__main__":
    ejecutarPruebaCarga()