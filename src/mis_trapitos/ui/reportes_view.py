import tkinter as tk
from tkinter import ttk, messagebox
from mis_trapitos.logica.generador_reporte import ReportGenerator

class ReportsView(tk.Frame):
    """
    Vista de Reportes y Estadísticas (Dashboard).
    Solo accesible por Administradores.
    Muestra KPIs y tablas detalladas de rendimiento.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.controller = ReportGenerator()
        
        self._configurarEstilos()
        self._crearInterfaz()
        self.cargarDatos()

    def _configurarEstilos(self):
        style = ttk.Style()
        style.configure("KPI.TLabel", font=("Segoe UI", 24, "bold"), foreground="#2C3E50")
        style.configure("KPITitle.TLabel", font=("Segoe UI", 10), foreground="#7F8C8D")
        style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), foreground="#2980B9")

    def _crearInterfaz(self):
        # 1. ENCABEZADO Y CONTROLES
        frame_top = tk.Frame(self, bg="white", pady=10, padx=20)
        frame_top.pack(fill="x")
        
        tk.Button(
            frame_top, text="🔄 Actualizar Datos", 
            bg="#34495E", fg="white", font=("Segoe UI", 10),
            command=self.cargarDatos
        ).pack(side="right")

        # 2. SECCIÓN DE KPIs
        # Un frame para mostrar metricas rapidas
        self.frame_kpis = tk.Frame(self, pady=10, padx=20)
        self.frame_kpis.pack(fill="x")
        
        # Tarjeta 1: Ventas Recientes
        self.lbl_kpi_ventas = self._crearTarjetaKPI(self.frame_kpis, "Ventas (Últimos 3 días)", "0")
        self.lbl_kpi_ventas.pack(side="left", padx=20)
        
        # Tarjeta 2: Mejor Descuento Activo
        self.lbl_kpi_oferta = self._crearTarjetaKPI(self.frame_kpis, "Mejor Oferta Actual", "N/A")
        self.lbl_kpi_oferta.pack(side="left", padx=20)
        
        # Tarjeta 3: Producto con Mayor Stock 
        self.lbl_kpi_stock = self._crearTarjetaKPI(self.frame_kpis, "Mayor Stock", "N/A")
        self.lbl_kpi_stock.pack(side="left", padx=20)

        # 3. PESTAÑAS DE DETALLE 
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Pestaña A: Ventas
        self.tab_ventas = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_ventas, text="📊 Rendimiento de Ventas")
        self._construirTabVentas()

        # Pestaña B: Inventario
        self.tab_inventario = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_inventario, text="📦 Salud de Inventario")
        self._construirTabInventario()

    def _crearTarjetaKPI(self, parent, titulo, valor_inicial):
        """Ayudante visual para crear tarjetas de métricas"""
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=20, pady=10)
        
        ttk.Label(frame, text=titulo, style="KPITitle.TLabel", background="white").pack(anchor="w")
        lbl_valor = ttk.Label(frame, text=valor_inicial, style="KPI.TLabel", background="white")
        lbl_valor.pack(anchor="w")
        
        return lbl_valor

    def _construirTabVentas(self):
        # Dividir en dos columnas
        frame_cols = tk.Frame(self.tab_ventas, bg="white")
        frame_cols.pack(fill="both", expand=True, padx=10, pady=10)

        # Columna 1: Top 10 Productos
        frame_c1 = tk.Frame(frame_cols, bg="white")
        frame_c1.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(frame_c1, text="Top 10 Productos (Últimos 30 días)", style="Section.TLabel", background="white").pack(anchor="w", pady=5)
        
        cols_top = ("desc", "total")
        self.tree_top = ttk.Treeview(frame_c1, columns=cols_top, show="headings", height=8)
        self.tree_top.heading("desc", text="Producto")
        self.tree_top.heading("total", text="Unidades Vendidas")
        self.tree_top.column("desc", width=250)
        self.tree_top.column("total", width=100, anchor="center")
        self.tree_top.pack(fill="both", expand=True)

        # Columna 2: Metodos de Pago
        frame_c2 = tk.Frame(frame_cols, bg="white")
        frame_c2.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(frame_c2, text="Uso de Métodos de Pago", style="Section.TLabel", background="white").pack(anchor="w", pady=5)
        
        cols_pago = ("metodo", "cantidad")
        self.tree_pagos = ttk.Treeview(frame_c2, columns=cols_pago, show="headings", height=8)
        self.tree_pagos.heading("metodo", text="Método")
        self.tree_pagos.heading("cantidad", text="Transacciones")
        self.tree_pagos.column("metodo", width=200)
        self.tree_pagos.column("cantidad", width=100, anchor="center")
        self.tree_pagos.pack(fill="both", expand=True)

    def _construirTabInventario(self):
        # Lista de productos estancados
        frame_content = tk.Frame(self.tab_inventario, bg="white", padx=10, pady=10)
        frame_content.pack(fill="both", expand=True)
        
        ttk.Label(frame_content, text="⚠️ Productos Estancados (Sin ventas en 90 días)", style="Section.TLabel", background="white").pack(anchor="w", pady=5)
        
        cols_est = ("desc", "talla", "color")
        self.tree_estancados = ttk.Treeview(frame_content, columns=cols_est, show="headings")
        self.tree_estancados.heading("desc", text="Producto")
        self.tree_estancados.heading("talla", text="Talla")
        self.tree_estancados.heading("color", text="Color")
        self.tree_estancados.pack(fill="both", expand=True)

    def cargarDatos(self):
        """Llama al controlador para refrescar toda la información"""
        # 1. Cargar KPIs
        metricas = self.controller.obtenerMetricasRapidas()
        self.lbl_kpi_ventas.config(text=str(metricas.get("ventas_recientes", 0)))
        self.lbl_kpi_oferta.config(text=metricas.get("mejor_descuento", "N/A"))
        
        mayor_stock = self.controller.obtenerResumenInventario()
        if mayor_stock:
            texto_stock = f"{mayor_stock['stock']} u.\n({mayor_stock['producto'][:15]}...)"
            self.lbl_kpi_stock.config(text=texto_stock, font=("Segoe UI", 12, "bold"))
        else:
            self.lbl_kpi_stock.config(text="Inventario Vacío")

        # 2. Cargar Tablas Ventas
        self._llenarTabla(self.tree_top, self.controller.obtenerTopVentasMes())
        self._llenarTabla(self.tree_pagos, self.controller.obtenerTendenciasPago())

        # 3. Cargar Tabla Inventario (Estancados)
        self._llenarTabla(self.tree_estancados, self.controller.obtenerProductosEstancados(90))

    def _llenarTabla(self, tree, datos):
        for item in tree.get_children():
            tree.delete(item)
        if datos:
            for row in datos:
                tree.insert("", "end", values=row)