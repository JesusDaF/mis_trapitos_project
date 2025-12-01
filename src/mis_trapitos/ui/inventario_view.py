import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from mis_trapitos.logica.producto_control import ProductController

class InventoryView(tk.Frame):
    """
    Vista de Gestión de Inventario (RF-1.1, RF-1.2).
    Permite visualizar el catálogo, filtrar productos y registrar nuevos items.
    """

    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        self.controller = ProductController()
        
        # Configuración de estilos para la tabla
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

        self._crearInterfaz()
        self.cargarDatosTabla() # Cargar datos al iniciar

    def _crearInterfaz(self):
        """Construye la barra de herramientas y la tabla de datos"""
        
        # --- 1. BARRA DE HERRAMIENTAS (Top) ---
        frame_toolbar = tk.Frame(self, bg="white", pady=10, padx=10)
        frame_toolbar.pack(fill="x")

        # Botón Nuevo Producto
        btn_nuevo = tk.Button(
            frame_toolbar, 
            text="+ Nuevo Producto", 
            bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalNuevoProducto
        )
        btn_nuevo.pack(side="left", padx=5)

        # Botón Refrescar
        btn_refresh = tk.Button(
            frame_toolbar, 
            text="🔄 Actualizar", 
            bg="#34495E", fg="white", font=("Segoe UI", 10),
            command=self.cargarDatosTabla
        )
        btn_refresh.pack(side="left", padx=5)

        # --- 2. TABLA DE DATOS (Treeview) ---
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # Definición de columnas
        columnas = ("producto", "talla", "color", "stock", "precio")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        # Encabezados
        self.tree.heading("producto", text="Descripción Producto")
        self.tree.heading("talla", text="Talla")
        self.tree.heading("color", text="Color")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("precio", text="Precio Base")

        # Anchos de columna
        self.tree.column("producto", width=300)
        self.tree.column("talla", width=80, anchor="center")
        self.tree.column("color", width=100, anchor="center")
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("precio", width=100, anchor="e") # Alineado a la derecha

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargarDatosTabla(self):
        """Solicita el catálogo al controlador y llena la tabla"""
        # 1. Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Obtener datos
        # datos = [(descripcion, talla, color, stock, precio), ...]
        datos = self.controller.obtenerCatalogo()
        
        # 3. Llenar filas
        for fila in datos:
            # Formatear precio con signo de pesos
            fila_visual = list(fila)
            fila_visual[4] = f"${fila[4]:.2f}" 
            
            self.tree.insert("", "end", values=fila_visual)

    # --- LÓGICA DEL FORMULARIO DE ALTA ---

    def _abrirModalNuevoProducto(self):
        """Abre una ventana emergente para registrar productos"""
        VentanaAltaProducto(self)

# --- CLASE AUXILIAR: VENTANA MODAL DE REGISTRO ---
class VentanaAltaProducto(Toplevel):
    """Sub-ventana para el formulario de alta de producto"""
    
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.view = parent_view # Referencia a la vista principal para refrescarla
        self.title("Nuevo Producto")
        self.geometry("400x550")
        self.configure(bg="white")
        
        # Hacemos que la ventana sea modal (bloquea la de atrás)
        self.transient(parent_view)
        self.grab_set()
        
        self._construirFormulario()

    def _construirFormulario(self):
        tk.Label(self, text="Registrar Nuevo Producto", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)

        # Campos
        frame_form = tk.Frame(self, bg="white", padx=20)
        frame_form.pack(fill="both", expand=True)

        # Categoría (Por simplicidad usaremos un Entry, idealmente sería un Combobox)
        tk.Label(frame_form, text="Nombre Categoría (Ej. Playeras):", bg="white").pack(anchor="w")
        self.entry_cat = tk.Entry(frame_form)
        self.entry_cat.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Descripción Producto:", bg="white").pack(anchor="w")
        self.entry_desc = tk.Entry(frame_form)
        self.entry_desc.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Precio Base ($):", bg="white").pack(anchor="w")
        self.entry_precio = tk.Entry(frame_form)
        self.entry_precio.pack(fill="x", pady=(0, 10))

        # Variantes Iniciales
        tk.Label(frame_form, text="--- Inventario Inicial ---", bg="white", fg="#7F8C8D").pack(pady=10)
        
        tk.Label(frame_form, text="Talla (Ej. M):", bg="white").pack(anchor="w")
        self.entry_talla = tk.Entry(frame_form)
        self.entry_talla.pack(fill="x")
        
        tk.Label(frame_form, text="Color (Ej. Rojo):", bg="white").pack(anchor="w")
        self.entry_color = tk.Entry(frame_form)
        self.entry_color.pack(fill="x")
        
        tk.Label(frame_form, text="Cantidad Inicial:", bg="white").pack(anchor="w")
        self.entry_stock = tk.Entry(frame_form)
        self.entry_stock.pack(fill="x")

        # Botón Guardar
        tk.Button(
            self, text="GUARDAR PRODUCTO", 
            bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=20, pady=20)

    def _guardar(self):
        # 1. Recolección de datos
        cat_nombre = self.entry_cat.get()
        desc = self.entry_desc.get()
        precio = self.entry_precio.get()
        
        talla = self.entry_talla.get()
        color = self.entry_color.get()
        stock = self.entry_stock.get()

        # 2. Lógica rápida para crear categoría al vuelo (Simplificación para UX)
        # Aquí intentamos crearla primero.
        id_empleado = self.view.usuario['id'] # Obtenemos el ID del usuario logueado
        
        # Instancia temporal del controlador para esta ventana
        ctrl = self.view.controller 
        
        # A. Crear Categoría
        # Intentamos crearla. Si ya existe, no pasa nada grave, el controlador lo maneja.
        # Necesitamos el ID de la categoría. Como nuestra función crearNuevaCategoria
        # devuelve True/False, haremos una pequeña trampa buscando todas las categorías
        # para encontrar el ID de la que escribimos.
        
        ctrl.crearNuevaCategoria(id_empleado, cat_nombre, "General")
        
        # Buscar el ID de la categoría (esto debería optimizarse en el futuro)
        cats = ctrl.inv_queries.obtenerCategorias()
        id_cat = next((c[0] for c in cats if c[1].lower() == cat_nombre.lower()), None)
        
        if not id_cat:
            messagebox.showerror("Error", "No se pudo gestionar la categoría.")
            return

        # B. Preparar variante
        lista_variantes = [{
            'talla': talla,
            'color': color,
            'stock': stock
        }]

        # C. Guardar Producto
        exito, msg = ctrl.registrarProductoNuevo(id_empleado, id_cat, desc, precio, lista_variantes)

        if exito:
            messagebox.showinfo("Éxito", msg)
            self.view.cargarDatosTabla() # Refrescar la tabla de atrás
            self.destroy() # Cerrar ventana modal
        else:
            messagebox.showerror("Error", msg)