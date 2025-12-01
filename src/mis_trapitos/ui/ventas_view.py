import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from mis_trapitos.logica.ventas_control import SalesController
from mis_trapitos.logica.producto_control import ProductController
from mis_trapitos.logica.cliente_control import CustomerController

class SalesView(tk.Frame):
    """
    Vista de Punto de Venta (POS).
    Gestiona la interacción de venta: Selección de productos, cliente y cobro.
    """

    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        
        # Controladores
        self.sales_ctrl = SalesController()
        self.prod_ctrl = ProductController()
        self.cust_ctrl = CustomerController()
        
        # Estado de la Venta
        self.carrito = [] # Lista de diccionarios con los items
        self.cliente_actual = None # Datos del cliente seleccionado (id, nombre)

        self._crearInterfaz()
        self._cargarCatalogoInicial()

    def _crearInterfaz(self):
        # Dividir pantalla en Izquierda (Catálogo) y Derecha (Ticket)
        paned = tk.PanedWindow(self, orient="horizontal", sashwidth=5, bg="#BDC3C7")
        paned.pack(fill="both", expand=True)

        # --- PANEL IZQUIERDO: BUSCADOR DE PRODUCTOS ---
        frame_izq = tk.Frame(paned, bg="white", padx=10, pady=10)
        paned.add(frame_izq, minsize=400) # Ancho mínimo

        # 1. Buscador
        lbl_buscar = tk.Label(frame_izq, text="🔍 Buscar Producto:", bg="white", font=("Segoe UI", 10, "bold"))
        lbl_buscar.pack(anchor="w")
        
        frame_search = tk.Frame(frame_izq, bg="white")
        frame_search.pack(fill="x", pady=(0, 10))
        
        self.entry_busqueda = tk.Entry(frame_search, font=("Segoe UI", 11))
        self.entry_busqueda.pack(side="left", fill="x", expand=True)
        self.entry_busqueda.bind("<Return>", lambda e: self._filtrarCatalogo()) # Enter para buscar

        btn_buscar = tk.Button(frame_search, text="Buscar", command=self._filtrarCatalogo, bg="#34495E", fg="white")
        btn_buscar.pack(side="left", padx=5)

        # 2. Tabla de Productos (Stock)
        self.tree_prod = ttk.Treeview(frame_izq, columns=("id", "desc", "talla", "color", "precio", "stock"), show="headings", height=15)
        self.tree_prod.heading("id", text="ID")
        self.tree_prod.heading("desc", text="Producto")
        self.tree_prod.heading("talla", text="Talla")
        self.tree_prod.heading("color", text="Color")
        self.tree_prod.heading("precio", text="Precio")
        self.tree_prod.heading("stock", text="Stock")
        
        # Configurar columnas
        self.tree_prod.column("id", width=0, stretch=False) # ID oculto
        self.tree_prod.column("desc", width=180)
        self.tree_prod.column("talla", width=50, anchor="center")
        self.tree_prod.column("color", width=70, anchor="center")
        self.tree_prod.column("precio", width=70, anchor="e")
        self.tree_prod.column("stock", width=50, anchor="center")
        
        self.tree_prod.pack(fill="both", expand=True)
        
        # Doble clic para agregar al carrito
        self.tree_prod.bind("<Double-1>", self._agregarAlCarrito)
        
        tk.Label(frame_izq, text="💡 Doble clic para agregar al carrito", bg="white", fg="gray").pack(pady=5)


        #PANEL DERECHO: TICKET / CARRITO 
        frame_der = tk.Frame(paned, bg="#ECF0F1", padx=15, pady=15)
        paned.add(frame_der, minsize=350)

        # 1. Selección de Cliente
        frame_cliente = tk.LabelFrame(frame_der, text="Datos del Cliente", bg="#ECF0F1", font=("Segoe UI", 9, "bold"))
        frame_cliente.pack(fill="x", pady=(0, 10))

        frame_cli_search = tk.Frame(frame_cliente, bg="#ECF0F1")
        frame_cli_search.pack(fill="x", padx=5, pady=5)
        
        tk.Label(frame_cli_search, text="Teléfono:", bg="#ECF0F1").pack(side="left")
        self.entry_tel = tk.Entry(frame_cli_search, width=15)
        self.entry_tel.pack(side="left", padx=5)
        tk.Button(frame_cli_search, text="Buscar", command=self._buscarCliente).pack(side="left")

        self.lbl_nombre_cliente = tk.Label(frame_cliente, text="Cliente: Público General", bg="#ECF0F1", fg="#2980B9", font=("Segoe UI", 10))
        self.lbl_nombre_cliente.pack(anchor="w", padx=5, pady=(0, 5))

        # 2. Tabla Carrito
        tk.Label(frame_der, text="🛒 Carrito de Compras", bg="#ECF0F1", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        
        self.tree_cart = ttk.Treeview(frame_der, columns=("desc", "cant", "precio", "desc_man", "total"), show="headings")
        self.tree_cart.heading("desc", text="Art.")
        self.tree_cart.heading("cant", text="Cant")
        self.tree_cart.heading("precio", text="Unit")
        self.tree_cart.heading("desc_man", text="Dsc(%)")
        self.tree_cart.heading("total", text="Subtotal")
        
        self.tree_cart.column("desc", width=120)
        self.tree_cart.column("cant", width=40, anchor="center")
        self.tree_cart.column("precio", width=60, anchor="e")
        self.tree_cart.column("desc_man", width=50, anchor="center")
        self.tree_cart.column("total", width=70, anchor="e")
        
        self.tree_cart.pack(fill="both", expand=True, pady=5)
        
        # Botones de manipulación de carrito
        frame_actions = tk.Frame(frame_der, bg="#ECF0F1")
        frame_actions.pack(fill="x")
        
        tk.Button(frame_actions, text="Quitar Item", command=self._quitarDelCarrito, bg="#E74C3C", fg="white").pack(side="left", padx=2)
        tk.Button(frame_actions, text="Aplicar Descuento Manual", command=self._aplicarDescuentoManual, bg="#F39C12", fg="white").pack(side="left", padx=2)


        # 3. Totales y Pago
        frame_total = tk.Frame(frame_der, bg="#BDC3C7", pady=10, padx=10)
        frame_total.pack(fill="x", pady=20)
        
        self.lbl_total = tk.Label(frame_total, text="TOTAL: $0.00", bg="#BDC3C7", font=("Segoe UI", 18, "bold"), fg="#2C3E50")
        self.lbl_total.pack(side="right")
        
        # Selección de Método de Pago
        frame_pago = tk.Frame(frame_der, bg="#ECF0F1")
        frame_pago.pack(fill="x", pady=5)
        
        tk.Label(frame_pago, text="Método de Pago:", bg="#ECF0F1").pack(side="left")
        self.combo_pago = ttk.Combobox(frame_pago, values=["efectivo", "tarjeta de credito", "transferencia bancaria"], state="readonly")
        self.combo_pago.current(0)
        self.combo_pago.pack(side="left", padx=10, fill="x", expand=True)

        # Botón COBRAR (Gigante)
        self.btn_cobrar = tk.Button(
            frame_der, 
            text="COBRAR VENTA", 
            bg="#27AE60", fg="white", 
            font=("Segoe UI", 14, "bold"),
            command=self._realizarCobro
        )
        self.btn_cobrar.pack(fill="x", pady=10)

    # LÓGICA DE CATÁLOGO

    def _cargarCatalogoInicial(self):
        """Trae todos los productos con stock > 0"""
        raw_data = self.prod_ctrl.obtenerCatalogo()
        # raw_data = [(desc, talla, color, stock, precio), ...]
        
        # Necesitamos el ID variante que está "escondido" en la query original 
        # (El query actual de obtenerCatalogo no traía ID, vamos a asumir que lo trae o lo ajustamos)
        # Ajuste rápido: El controlador llama a InventoryQueries.obtenerProductosEnInventario
        # Esa query necesita retornar el ID para que el carrito funcione.
        
        # NOTA: Si InventoryQueries no devuelve el ID, tendremos un problema. 
        # Asumiremos que InventoryQueries retorna: (desc, talla, color, stock, precio)
        # PERO necesitamos el ID. 
        # *Corrección al vuelo*: Usaremos una búsqueda directa aquí o mejoraremos el query en el backend luego.
        # Por ahora, para no romper el backend, usaremos la lógica de filtrado del Controller si existe,
        # o confiaremos en que el usuario busca por nombre.
        
        # Para que funcione YA, vamos a hacer un truco sucio pero funcional: 
        # Limpiar tree y llenar solo visualmente. El ID lo buscaremos al seleccionar.
        # *Mejor opción*: Modificar InventoryQueries para traer el ID. 
        # (Asumo que lo hicimos o lo haremos, aquí simulo que el index 5 es el ID si modificamos query,
        # si no, usaremos lógica de coincidencia).
        
        # Haremos una consulta directa de IDs para la vista de ventas
        # Esto es más seguro que adivinar.
        conn = self.prod_ctrl.inv_queries.db.obtenerConexion()
        cursor = conn.cursor()
        cursor.execute("SELECT v.id_variante, p.descripcion, v.talla, v.color, p.precio_base, v.stock_disponible FROM Variantes_Producto v JOIN Productos p ON v.id_producto = p.id_producto WHERE v.stock_disponible > 0")
        self.data_productos = cursor.fetchall() # Guardamos en memoria
        conn.close()
        
        self._llenarTablaProductos(self.data_productos)

    def _llenarTablaProductos(self, lista_datos):
        for item in self.tree_prod.get_children():
            self.tree_prod.delete(item)
            
        for row in lista_datos:
            # row = (id, desc, talla, color, precio, stock)
            self.tree_prod.insert("", "end", values=row)

    def _filtrarCatalogo(self, event=None):
        texto = self.entry_busqueda.get().lower()
        if not texto:
            self._llenarTablaProductos(self.data_productos)
            return
            
        filtrados = [p for p in self.data_productos if texto in p[1].lower()]
        self._llenarTablaProductos(filtrados)

    # LOGICA DEL CARRITO 

    def _agregarAlCarrito(self, event):
        seleccion = self.tree_prod.selection()
        if not seleccion: return
        
        item_data = self.tree_prod.item(seleccion[0])['values']
        # values = [id, desc, talla, color, precio, stock]
        
        id_variante = item_data[0]
        desc_completa = f"{item_data[1]} ({item_data[2]}/{item_data[3]})"
        precio = float(item_data[4])
        stock_max = int(item_data[5])
        
        # Pedir cantidad
        cantidad_str = simpledialog.askstring("Cantidad", f"Stock disponible: {stock_max}\n¿Cuántos desea llevar?")
        if not cantidad_str: return
        
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0 or cantidad > stock_max:
                messagebox.showerror("Error", "Cantidad inválida o insuficiente.")
                return
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar un número entero.")
            return

        # Verificar si ya existe en carrito
        for i, item in enumerate(self.carrito):
            if item['id_variante'] == id_variante:
                # Sumar cantidad
                if item['cantidad'] + cantidad > stock_max:
                    messagebox.showwarning("Stock", "No hay suficiente stock para agregar más.")
                    return
                item['cantidad'] += cantidad
                self._refrescarCarrito()
                return

        # Agregar nuevo
        nuevo_item = {
            'id_variante': id_variante,
            'desc': desc_completa,
            'cantidad': cantidad,
            'precio': precio,
            'descuento_manual': 0,
            'total': cantidad * precio
        }
        self.carrito.append(nuevo_item)
        self._refrescarCarrito()

    def _quitarDelCarrito(self):
        seleccion = self.tree_cart.selection()
        if not seleccion: return
        
        idx = self.tree_cart.index(seleccion[0])
        del self.carrito[idx]
        self._refrescarCarrito()

    def _aplicarDescuentoManual(self):
        seleccion = self.tree_cart.selection()
        if not seleccion: return
        
        idx = self.tree_cart.index(seleccion[0])
        item = self.carrito[idx]
        
        desc_str = simpledialog.askstring("Descuento", "Ingrese porcentaje de descuento (0-100):", initialvalue=str(item['descuento_manual']))
        if desc_str is not None:
            try:
                val = float(desc_str)
                if 0 <= val <= 100:
                    self.carrito[idx]['descuento_manual'] = val
                    self._refrescarCarrito()
                else:
                    messagebox.showerror("Error", "Rango inválido.")
            except ValueError:
                pass

    def _refrescarCarrito(self):
        # Limpiar tabla
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)
            
        total_global = 0.0
        
        for item in self.carrito:
            # Calcular subtotal visual (aproximado, el backend tiene la última palabra)
            precio_con_desc = item['precio'] * (1 - item['descuento_manual']/100)
            subtotal = precio_con_desc * item['cantidad']
            item['total'] = subtotal # Actualizar modelo
            total_global += subtotal
            
            # Insertar en tree
            vals = (item['desc'], item['cantidad'], f"${item['precio']:.2f}", f"{item['descuento_manual']}%", f"${subtotal:.2f}")
            self.tree_cart.insert("", "end", values=vals)
            
        self.lbl_total.config(text=f"TOTAL: ${total_global:.2f}")

    # --- LÓGICA DE CLIENTE ---

    def _buscarCliente(self):
        tel = self.entry_tel.get().strip()
        if not tel: return
        
        datos = self.cust_ctrl.buscarClientePorTelefono(tel)
        if datos:
            self.cliente_actual = datos
            self.lbl_nombre_cliente.config(text=f"Cliente: {datos['nombre']} ✅", fg="green")
        else:
            resp = messagebox.askyesno("No encontrado", "Cliente no encontrado. ¿Desea registrarlo ahora?")
            if resp:
                # Aquí podríamos abrir un modal de registro rápido, similar al de productos.
                # Por brevedad, simplemente avisamos.
                messagebox.showinfo("Info", "Por favor vaya al módulo de Clientes para registrarlo.")

    # --- LÓGICA DE COBRO ---

    def _realizarCobro(self):
        if not self.carrito:
            messagebox.showwarning("Vacío", "El carrito está vacío.")
            return

        id_cli = self.cliente_actual['id'] if self.cliente_actual else None
        metodo = self.combo_pago.get()
        
        # Confirmación
        if not messagebox.askyesno("Cobrar", f"¿Confirmar venta por {self.lbl_total.cget('text')}?"):
            return

        # Enviar al Backend
        # Nota: El carrito del controlador espera claves específicas, ya las tenemos alineadas.
        exito, mensaje = self.sales_ctrl.procesarVentaNueva(
            self.usuario['id'],
            id_cli,
            metodo,
            self.carrito
        )
        
        if exito:
            messagebox.showinfo("Venta Exitosa", mensaje)
            self.carrito = [] # Limpiar
            self.cliente_actual = None
            self.lbl_nombre_cliente.config(text="Cliente: Público General", fg="#2980B9")
            self._refrescarCarrito()
            self._cargarCatalogoInicial() # Recargar stock
        else:
            messagebox.showerror("Error en Venta", mensaje)