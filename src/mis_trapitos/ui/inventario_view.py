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

        # Boton de Ofertas
        tk.Button(
            frame_toolbar, 
            text="🏷️Crear Oferta", 
            bg="#EFD61F", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalOferta
        ).pack(side="left", padx=5)

        # Botón Refrescar
        btn_refresh = tk.Button(
            frame_toolbar, 
            text="🔄 Actualizar", 
            bg="#34495E", fg="white", font=("Segoe UI", 10),
            command=self.cargarDatosTabla
        )
        btn_refresh.pack(side="left", padx=5)

        # BOTON ASIGNAR PROVEEDOR
        tk.Button(
            frame_toolbar, 
            text="🔗 Asignar Proveedor", 
            bg="#F39C12", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalVincular
        ).pack(side="left", padx=5)
        
        # BOTON VISUALIZAR PROVEEDORES
        tk.Button(
            frame_toolbar, 
            text=" Ver Proveedores", 
            bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold"), 
            command=self._abrirModalVerProveedores
        ).pack(side="left", padx=5)

        # BOTÓN EDICIÓN
        tk.Button(
            frame_toolbar, 
            text="✏️ Editar / Resurtir", 
            bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalEdicion
        ).pack(side="left", padx=5)

        # BOTON ELIMINAR
        tk.Button(
            frame_toolbar, text="🗑️ Eliminar", 
            bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._accionEliminar
        ).pack(side="left", padx=5)

        # --- 2. TABLA DE DATOS (Treeview) ---
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # Definición de columnas
        columnas = ("id_var", "id", "producto", "talla", "color", "stock", "precio") 
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        # ID 
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=40, anchor="center")
        
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
        # 1. Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Obtener datos 
        datos = self.controller.obtenerCatalogo()
        
        # 3. Configurar qué columnas se ven y cuáles se ocultan
        # Ocultamos "id_var" y "id_prod"
        self.tree["displaycolumns"] = ("producto", "talla", "color", "stock", "precio")
        
        # 4. Llenar filas
        for fila in datos:
            # fila = (id_var, id_prod, desc, talla, color, stock, precio)
            fila_visual = list(fila)
            
            # Formatear precio 
            fila_visual[6] = f"${fila[6]:.2f}" 
            
            self.tree.insert("", "end", values=fila_visual)

    # LÓGICA DEL FORMULARIO DE ALTA 
    def _abrirModalVincular(self):
        """Abre el modal para relacionar un producto con un proveedor"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla primero.")
            return

        # Obtenemos datos del producto seleccionado
        item_id = self.tree.item(seleccion[0])['values'][0] # ID Producto
        desc_prod = self.tree.item(seleccion[0])['values'][1] # Descripción
        
        VentanaVincularProveedor(self, item_id, desc_prod)

    def _abrirModalNuevoProducto(self):
        """Abre una ventana emergente para registrar productos"""
        VentanaAltaProducto(self)

    def _abrirModalOferta(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para aplicarle descuento.")
            return

        # Obtenemos datos del producto seleccionado
        # Recordando que el query actualizado devuelve:
        # (id_variante, id_producto, desc, talla, color, stock, precio)
        valores = self.tree.item(seleccion[0])['values']
        
        id_producto = valores[1] # El ID del producto padre
        nombre_prod = valores[2]
        
        VentanaCrearOferta(self, id_producto, nombre_prod)

    def _abrirModalEdicion(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para editar.")
            return

        # Obtenemos datos actuales de la fila seleccionada
        # values = (id, desc, talla, color, stock, precio_fmt)
        valores = self.tree.item(seleccion[0])['values']
        
        id_prod = valores[0]
        desc = valores[1]
        VentanaEdicionProducto(self, valores)

    def _accionEliminar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para eliminar.")
            return

        # Pedir confirmación
        if not messagebox.askyesno("Confirmar Eliminación", "⚠️ ¿Está seguro de eliminar este producto?\nSe borrarán todas sus variantes y stock"):
            return

        # Obtener ID (Recordando el ajuste de columnas: id_var, id_prod...)
        valores = self.tree.item(seleccion[0])['values']
        id_producto = valores[1] # ID del producto padre

        exito, msg = self.controller.eliminarProducto(self.usuario['id'], id_producto)
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargarDatosTabla()
        else:
            messagebox.showerror("Error", msg)

    def _abrirModalVerProveedores(self):
        """Abre una ventana que lista los proveedores del producto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para ver sus proveedores.")
            return

        # Obtenemos el ID del producto (recuerda que ya configuramos la columna ID oculta/visible)
        item_data = self.tree.item(seleccion[0])['values']
        id_producto = item_data[0] 
        nombre_producto = item_data[1]
        
        VentanaListaProveedores(self, id_producto, nombre_producto)

# CLASE AUXILIAR: VENTANA MODAL DE REGISTRO
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

from datetime import datetime, timedelta

class VentanaCrearOferta(Toplevel):
    def __init__(self, parent_view, id_producto, nombre_producto):
        super().__init__(parent_view)
        self.view = parent_view
        self.id_producto = id_producto
        self.title("Configurar Promoción")
        self.geometry("350x400")
        self.configure(bg="white")
        self.transient(parent_view)
        self.grab_set()

        self._construirFormulario(nombre_producto)

    def _construirFormulario(self, nombre):
        tk.Label(self, text="Nueva Oferta / Descuento", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        tk.Label(self, text=f"Producto: {nombre}", bg="white", fg="gray").pack()

        frame = tk.Frame(self, bg="white", padx=20, pady=10)
        frame.pack(fill="both")

        # Campo Porcentaje
        tk.Label(frame, text="Porcentaje de Descuento (%):", bg="white").pack(anchor="w")
        self.entry_porc = tk.Entry(frame, font=("Segoe UI", 12))
        self.entry_porc.pack(fill="x", pady=(0, 15))

        # Fechas (Pre-llenadas para facilitar uso)
        hoy = datetime.now().strftime("%Y-%m-%d")
        futuro = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        tk.Label(frame, text="Fecha Inicio (AAAA-MM-DD):", bg="white").pack(anchor="w")
        self.entry_inicio = tk.Entry(frame, font=("Segoe UI", 12))
        self.entry_inicio.insert(0, hoy)
        self.entry_inicio.pack(fill="x", pady=(0, 15))

        tk.Label(frame, text="Fecha Fin (AAAA-MM-DD):", bg="white").pack(anchor="w")
        self.entry_fin = tk.Entry(frame, font=("Segoe UI", 12))
        self.entry_fin.insert(0, futuro)
        self.entry_fin.pack(fill="x", pady=(0, 15))
        
        tk.Label(frame, text="* El descuento se aplicará automáticamente en caja.", bg="white", fg="#E67E22", font=("Segoe UI", 8)).pack()

        tk.Button(
            self, text="ACTIVAR OFERTA", 
            bg="#E67E22", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=20, pady=20)

    def _guardar(self):
        porc = self.entry_porc.get()
        ini = self.entry_inicio.get()
        fin = self.entry_fin.get()
        
        # Llamamos al ProductController (que ya tiene el método agregarOferta)
        exito, msg = self.view.controller.agregarOferta(
            self.id_producto, porc, ini, fin
        )
        
        if exito:
            messagebox.showinfo("Oferta Creada", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class VentanaVincularProveedor(Toplevel):
    """Sub-ventana para vincular proveedores y productos"""
    def __init__(self, parent_view, id_producto, nombre_producto):
        super().__init__(parent_view)
        self.view = parent_view
        self.id_producto = id_producto
        self.title("Asignar Proveedor")
        self.geometry("400x250")
        self.configure(bg="white")
        self.transient(parent_view)
        self.grab_set()
        
        self.lista_provs = [] # Para guardar (id, nombre)
        self._construirFormulario(nombre_producto)

    def _construirFormulario(self, nombre_producto):
        tk.Label(self, text="Vincular Proveedor", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        tk.Label(self, text=f"Producto: {nombre_producto}", bg="white", fg="gray").pack()

        tk.Label(self, text="Seleccione Proveedor:", bg="white").pack(anchor="w", padx=20, pady=(20, 5))
        
        # Obtener lista de proveedores del controlador
        raw_provs = self.view.controller.obtenerListaProveedores()
        # raw_provs = [(id, nombre, contacto), ...]
        self.lista_provs = raw_provs
        nombres = [f"{p[1]} (ID: {p[0]})" for p in raw_provs]
        
        self.combo_prov = ttk.Combobox(self, values=nombres, state="readonly", width=40)
        self.combo_prov.pack(padx=20)

        tk.Button(
            self, text="VINCULAR", 
            bg="#F39C12", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=40, pady=30)

    def _guardar(self):
        idx = self.combo_prov.current()
        if idx == -1:
            messagebox.showwarning("Error", "Seleccione un proveedor.")
            return
            
        id_proveedor = self.lista_provs[idx][0]
        
        # Llamamos al controlador
        exito, msg = self.view.controller.vincularProductoAProveedor(
            self.view.usuario['id'],
            id_proveedor,
            self.id_producto
        )
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
    
class VentanaListaProveedores(Toplevel):
    """
    Popup que muestra la relación N:M (Qué proveedores surten este producto).
    """
    def __init__(self, parent_view, id_producto, nombre_producto):
        super().__init__(parent_view)
        self.view = parent_view
        self.title(f"Proveedores de: {nombre_producto}")
        self.geometry("500x300")
        self.configure(bg="white")
        
        # UI Limpia
        tk.Label(
            self, 
            text=f"Proveedores Asociados a:\n{nombre_producto}", 
            font=("Segoe UI", 12, "bold"), 
            bg="white", fg="#2C3E50"
        ).pack(pady=10)

        # Tabla de Proveedores
        frame_tabla = tk.Frame(self, bg="white", padx=10, pady=10)
        frame_tabla.pack(fill="both", expand=True)

        cols = ("empresa", "contacto")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
        
        self.tree.heading("empresa", text="Empresa / Proveedor")
        self.tree.heading("contacto", text="Datos de Contacto")
        
        self.tree.column("empresa", width=200)
        self.tree.column("contacto", width=250)
        
        self.tree.pack(fill="both", expand=True)
        
        # Botón Cerrar
        tk.Button(
            self, text="Cerrar", command=self.destroy,
            bg="#95A5A6", fg="white"
        ).pack(pady=10)

        self._cargarDatos(id_producto)

    def _cargarDatos(self, id_producto):
        """Consulta al controlador quiénes son los proveedores"""
        # Usamos el método que ya existe en ProductController
        lista = self.view.controller.obtenerProveedoresDeProducto(id_producto)
        
        if not lista:
            # Si la lista está vacía, mostramos un aviso en la tabla
            self.tree.insert("", "end", values=("(Sin proveedores asignados)", "-"))
        else:
            for prov in lista:
                # prov = (id, nombre, contacto) -> Ajustamos según lo que retorne tu query
                # Asumiendo que retorna (id, nombre, contacto)
                self.tree.insert("", "end", values=(prov[1], prov[2]))

class VentanaEdicionProducto(Toplevel):
    """Sub ventana para editar o resurtir entradas de productos en el inventario"""
    def __init__(self, parent_view, valores_fila):
        super().__init__(parent_view)
        self.view = parent_view
        self.title("Editar Producto / Resurtir")
        self.geometry("350x400")
        self.configure(bg="white")
        
        # Desempaquetar datos (según el query nuevo)
        self.id_variante = valores_fila[0]
        self.id_producto = valores_fila[1]
        desc = valores_fila[2]
        talla = valores_fila[3]
        color = valores_fila[4]
        stock_actual = valores_fila[5]
        precio_actual_str = valores_fila[6].replace("$", "")

        tk.Label(self, text="Editar Inventario", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        tk.Label(self, text=f"{desc}\n({talla} / {color})", bg="white", fg="gray").pack()

        frame = tk.Frame(self, bg="white", padx=20, pady=20)
        frame.pack(fill="both")

        # Campo Precio
        tk.Label(frame, text="Precio Base ($):", bg="white").pack(anchor="w")
        self.entry_precio = tk.Entry(frame, font=("Segoe UI", 12))
        self.entry_precio.insert(0, precio_actual_str)
        self.entry_precio.pack(fill="x", pady=(0, 15))

        # Campo Stock
        tk.Label(frame, text="Stock Disponible (Resurtir):", bg="white").pack(anchor="w")
        self.entry_stock = tk.Entry(frame, font=("Segoe UI", 12))
        self.entry_stock.insert(0, str(stock_actual))
        self.entry_stock.pack(fill="x", pady=(0, 15))

        tk.Button(
            self, text="GUARDAR CAMBIOS", 
            bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=20, pady=10)

    def _guardar(self):
        nuevo_precio = self.entry_precio.get()
        nuevo_stock = self.entry_stock.get()
        
        exito, msg = self.view.controller.actualizarProductoExistente(
            self.view.usuario['id'],
            self.id_producto,
            self.id_variante,
            nuevo_precio,
            nuevo_stock
        )
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.view.cargarDatosTabla()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)