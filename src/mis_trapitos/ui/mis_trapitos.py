"""
Sistema de Gestión Local - Mis Trapitos
Aplicación completa de punto de venta e inventario para tienda de ropa

Autores: Sanchez Rodriguez Karen Itzell, Dávalos Flores Jesús,
        Flores Sanchez Alexandra Guadalupe, Valadez Nuño Saúl,
        Lozano Garza Marco Antonio
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QStackedWidget, QFrame, QGroupBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QHeaderView, QTextEdit, QDateEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime

# ============================================================================
# VENTANA PRINCIPAL
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Inicializa la ventana principal del sistema
        """
        super().__init__()
        self.usuario_actual = "Admin"  # almacena el usuario logueado
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz principal
        """
        self.setWindowTitle("Mis Trapitos - Sistema de Gestión")
        self.setGeometry(100, 100, 1400, 800)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QHBoxLayout()
        widget_central.setLayout(layout_principal)
        
        # Panel lateral de navegación
        self.panel_navegacion = self.crearPanelNavegacion()
        layout_principal.addWidget(self.panel_navegacion)
        
        # Área de contenido
        self.area_contenido = QStackedWidget()
        layout_principal.addWidget(self.area_contenido)
        
        # Agregar vistas
        self.ventas_view = VentasView()
        self.inventario_view = InventarioView()
        self.clientes_view = ClientesView()
        self.proveedores_view = ProveedoresView()
        self.reportes_view = ReportesView()
        
        self.area_contenido.addWidget(self.ventas_view)
        self.area_contenido.addWidget(self.inventario_view)
        self.area_contenido.addWidget(self.clientes_view)
        self.area_contenido.addWidget(self.proveedores_view)
        self.area_contenido.addWidget(self.reportes_view)
        
        # Aplicar estilos
        self.aplicarEstilos()
        
    def crearPanelNavegacion(self):
        """
        Crea el panel lateral con opciones de navegación
        """
        panel = QFrame()
        panel.setMaximumWidth(220)
        panel.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Logo/Título
        titulo = QLabel("Mis Trapitos")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: white; padding: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Usuario actual
        label_usuario = QLabel(f"Usuario: {self.usuario_actual}")
        label_usuario.setStyleSheet("color: #ecf0f1; padding: 10px; font-size: 11px;")
        label_usuario.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_usuario)
        
        # Botones de navegación
        botones = [
            ("🛒 Ventas", 0, self.mostrarVentas),
            ("📦 Inventario", 1, self.mostrarInventario),
            ("👥 Clientes", 2, self.mostrarClientes),
            ("🚚 Proveedores", 3, self.mostrarProveedores),
            ("📊 Reportes", 4, self.mostrarReportes)
        ]
        
        for texto, index, funcion in botones:
            boton = QPushButton(texto)
            boton.clicked.connect(funcion)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)
            layout.addWidget(boton)
        
        layout.addStretch()
        
        # Botón cerrar sesión
        boton_cerrar = QPushButton("🚪 Cerrar Sesión")
        boton_cerrar.clicked.connect(self.cerrarSesion)
        boton_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px;
                margin: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(boton_cerrar)
        
        return panel
    
    def mostrarVentas(self):
        """
        Muestra la vista de ventas (POS)
        """
        self.area_contenido.setCurrentIndex(0)
        
    def mostrarInventario(self):
        """
        Muestra la vista de inventario
        """
        self.area_contenido.setCurrentIndex(1)
        
    def mostrarClientes(self):
        """
        Muestra la vista de clientes
        """
        self.area_contenido.setCurrentIndex(2)
        
    def mostrarProveedores(self):
        """
        Muestra la vista de proveedores
        """
        self.area_contenido.setCurrentIndex(3)
        
    def mostrarReportes(self):
        """
        Muestra la vista de reportes
        """
        self.area_contenido.setCurrentIndex(4)
        
    def cerrarSesion(self):
        """
        Cierra la sesión actual
        """
        respuesta = QMessageBox.question(
            self, 
            "Cerrar Sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.close()
        
    def aplicarEstilos(self):
        """
        Aplica estilos globales a la aplicación
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: white;
            }
        """)

# ============================================================================
# VISTA DE VENTAS (POS)
# ============================================================================

class VentasView(QWidget):
    def __init__(self):
        """
        Inicializa la vista de ventas
        """
        super().__init__()
        self.carrito = []  # almacena los productos agregados a la venta
        self.total_venta = 0.0  # almacena el valor total de la venta
        self.subtotal_venta = 0.0  # almacena el subtotal sin descuentos
        self.descuento_total = 0.0  # almacena el descuento total aplicado
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz de ventas
        """
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("🛒 Punto de Venta (POS)")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout_principal.addWidget(titulo)
        
        # Layout horizontal para búsqueda y carrito
        layout_horizontal = QHBoxLayout()
        layout_principal.addLayout(layout_horizontal)
        
        # Panel de búsqueda de productos
        panel_busqueda = self.crearPanelBusqueda()
        layout_horizontal.addWidget(panel_busqueda, 1)
        
        # Panel del carrito
        panel_carrito = self.crearPanelCarrito()
        layout_horizontal.addWidget(panel_carrito, 1)
        
        # Panel de totales y pago
        panel_pago = self.crearPanelPago()
        layout_principal.addWidget(panel_pago)
        
    def crearPanelBusqueda(self):
        """
        Crea el panel para buscar y agregar productos
        """
        grupo = QGroupBox("Búsqueda de Productos")
        layout = QVBoxLayout()
        grupo.setLayout(layout)
        
        # Barra de búsqueda
        layout_busqueda = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por código o nombre...")
        self.input_busqueda.returnPressed.connect(self.buscarProducto)
        layout_busqueda.addWidget(self.input_busqueda)
        
        boton_buscar = QPushButton("🔍 Buscar")
        boton_buscar.clicked.connect(self.buscarProducto)
        layout_busqueda.addWidget(boton_buscar)
        
        layout.addLayout(layout_busqueda)
        
        # Tabla de resultados
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(6)
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código", "Producto", "Categoría", "Precio", "Stock", "Acción"
        ])
        self.tabla_productos.horizontalHeader().setStretchLastSection(True)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_productos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_productos)
        
        # Cargar productos de ejemplo
        self.cargarProductosEjemplo()
        
        return grupo
    
    def crearPanelCarrito(self):
        """
        Crea el panel del carrito de compras
        """
        grupo = QGroupBox("Carrito de Compras")
        layout = QVBoxLayout()
        grupo.setLayout(layout)
        
        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(7)
        self.tabla_carrito.setHorizontalHeaderLabels([
            "Producto", "Precio", "Cantidad", "Descuento %", "Subtotal", "Eliminar", ""
        ])
        self.tabla_carrito.horizontalHeader().setStretchLastSection(True)
        self.tabla_carrito.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_carrito)
        
        # Botones de acción
        layout_botones = QHBoxLayout()
        
        boton_limpiar = QPushButton("🗑️ Limpiar Carrito")
        boton_limpiar.setStyleSheet("background-color: #e74c3c;")
        boton_limpiar.clicked.connect(self.limpiarCarrito)
        layout_botones.addWidget(boton_limpiar)
        
        layout.addLayout(layout_botones)
        
        return grupo
    
    def crearPanelPago(self):
        """
        Crea el panel de totales y métodos de pago
        """
        grupo = QGroupBox("Totales y Pago")
        layout = QHBoxLayout()
        grupo.setLayout(layout)
        
        # Panel de totales
        layout_totales = QVBoxLayout()
        
        self.label_subtotal = QLabel("Subtotal: $0.00")
        self.label_subtotal.setFont(QFont("Arial", 13))
        self.label_subtotal.setStyleSheet("color: #34495e;")
        layout_totales.addWidget(self.label_subtotal)
        
        self.label_descuento = QLabel("Descuento: $0.00")
        self.label_descuento.setFont(QFont("Arial", 13))
        self.label_descuento.setStyleSheet("color: #e67e22;")
        layout_totales.addWidget(self.label_descuento)
        
        self.label_total = QLabel("TOTAL: $0.00")
        self.label_total.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_total.setStyleSheet("color: #27ae60;")
        layout_totales.addWidget(self.label_total)
        
        layout.addLayout(layout_totales)
        
        # Panel de método de pago y cliente
        layout_derecha = QVBoxLayout()
        
        # Cliente opcional
        layout_cliente = QHBoxLayout()
        label_cliente = QLabel("Cliente (opcional):")
        layout_cliente.addWidget(label_cliente)
        
        self.combo_cliente = QComboBox()
        self.combo_cliente.addItems(["Sin cliente", "Cliente 1", "Cliente 2", "Cliente 3"])
        layout_cliente.addWidget(self.combo_cliente)
        
        boton_nuevo_cliente = QPushButton("+")
        boton_nuevo_cliente.setMaximumWidth(40)
        boton_nuevo_cliente.clicked.connect(self.registrarClienteRapido)
        layout_cliente.addWidget(boton_nuevo_cliente)
        
        layout_derecha.addLayout(layout_cliente)
        
        # Método de pago
        layout_metodo = QHBoxLayout()
        label_metodo = QLabel("Método de Pago:")
        layout_metodo.addWidget(label_metodo)
        
        self.combo_metodo_pago = QComboBox()
        self.combo_metodo_pago.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        layout_metodo.addWidget(self.combo_metodo_pago)
        
        layout_derecha.addLayout(layout_metodo)
        
        layout.addLayout(layout_derecha)
        
        # Botón confirmar venta
        boton_confirmar = QPushButton("✓ Confirmar Venta")
        boton_confirmar.clicked.connect(self.confirmarVenta)
        boton_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        layout.addWidget(boton_confirmar)
        
        return grupo
    
    def cargarProductosEjemplo(self):
        """
        Carga productos de ejemplo en la tabla
        """
        productos_ejemplo = [
            ("P001", "Camiseta Básica", "Camisetas", 150.00, 25),
            ("P002", "Pantalón Jean", "Pantalones", 450.00, 15),
            ("P003", "Sudadera Invernal", "Ropa de Invierno", 350.00, 10),
            ("P004", "Gorra Deportiva", "Accesorios", 120.00, 30),
            ("P005", "Playera Estampada", "Camisetas", 180.00, 20),
        ]
        
        self.tabla_productos.setRowCount(len(productos_ejemplo))
        
        for fila, producto in enumerate(productos_ejemplo):
            for columna, valor in enumerate(producto):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_productos.setItem(fila, columna, item)
            
            # Botón agregar
            boton_agregar = QPushButton("+ Agregar")
            boton_agregar.setStyleSheet("background-color: #2ecc71;")
            boton_agregar.clicked.connect(lambda checked, f=fila: self.agregarAlCarrito(f))
            self.tabla_productos.setCellWidget(fila, 5, boton_agregar)
    
    def buscarProducto(self):
        """
        Busca productos en la base de datos
        """
        termino_busqueda = self.input_busqueda.text().lower()
        
        for fila in range(self.tabla_productos.rowCount()):
            nombre = self.tabla_productos.item(fila, 1).text().lower()
            codigo = self.tabla_productos.item(fila, 0).text().lower()
            
            if termino_busqueda in nombre or termino_busqueda in codigo:
                self.tabla_productos.setRowHidden(fila, False)
            else:
                self.tabla_productos.setRowHidden(fila, True)
        
    def agregarAlCarrito(self, fila):
        """
        Agrega un producto al carrito
        """
        codigo = self.tabla_productos.item(fila, 0).text()
        nombre = self.tabla_productos.item(fila, 1).text()
        precio = float(self.tabla_productos.item(fila, 3).text())
        stock = int(self.tabla_productos.item(fila, 4).text())
        
        if stock <= 0:
            QMessageBox.warning(self, "Sin Stock", "Este producto no tiene stock disponible")
            return
        
        # Verificar si el producto ya está en el carrito
        for item in self.carrito:
            if item['codigo'] == codigo:
                item['cantidad'] += 1
                self.actualizarTablaCarrito()
                self.actualizarTotales()
                return
        
        # Agregar nuevo producto al carrito
        self.carrito.append({
            'codigo': codigo,
            'nombre': nombre,
            'precio': precio,
            'cantidad': 1,
            'descuento': 0
        })
        
        self.actualizarTablaCarrito()
        self.actualizarTotales()
        
    def actualizarTablaCarrito(self):
        """
        Actualiza la visualización del carrito
        """
        self.tabla_carrito.setRowCount(len(self.carrito))
        
        for fila, item in enumerate(self.carrito):
            # Nombre
            nombre_item = QTableWidgetItem(item['nombre'])
            nombre_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.tabla_carrito.setItem(fila, 0, nombre_item)
            
            # Precio
            precio_item = QTableWidgetItem(f"${item['precio']:.2f}")
            precio_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_carrito.setItem(fila, 1, precio_item)
            
            # Cantidad (editable con spinbox)
            spin_cantidad = QSpinBox()
            spin_cantidad.setMinimum(1)
            spin_cantidad.setMaximum(100)
            spin_cantidad.setValue(item['cantidad'])
            spin_cantidad.valueChanged.connect(lambda val, f=fila: self.cambiarCantidad(f, val))
            self.tabla_carrito.setCellWidget(fila, 2, spin_cantidad)
            
            # Descuento (editable con spinbox)
            spin_descuento = QSpinBox()
            spin_descuento.setMinimum(0)
            spin_descuento.setMaximum(100)
            spin_descuento.setValue(item['descuento'])
            spin_descuento.setSuffix("%")
            spin_descuento.valueChanged.connect(lambda val, f=fila: self.cambiarDescuento(f, val))
            self.tabla_carrito.setCellWidget(fila, 3, spin_descuento)
            
            # Subtotal
            subtotal = item['precio'] * item['cantidad']
            subtotal -= subtotal * (item['descuento'] / 100)
            subtotal_item = QTableWidgetItem(f"${subtotal:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignCenter)
            subtotal_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla_carrito.setItem(fila, 4, subtotal_item)
            
            # Botón eliminar
            boton_eliminar = QPushButton("🗑️")
            boton_eliminar.setStyleSheet("background-color: #e74c3c;")
            boton_eliminar.clicked.connect(lambda checked, f=fila: self.eliminarDelCarrito(f))
            self.tabla_carrito.setCellWidget(fila, 5, boton_eliminar)
    
    def cambiarCantidad(self, fila, cantidad):
        """
        Cambia la cantidad de un producto en el carrito
        """
        self.carrito[fila]['cantidad'] = cantidad
        self.actualizarTotales()
        self.actualizarTablaCarrito()
    
    def cambiarDescuento(self, fila, descuento):
        """
        Cambia el descuento de un producto en el carrito
        """
        self.carrito[fila]['descuento'] = descuento
        self.actualizarTotales()
        self.actualizarTablaCarrito()
    
    def eliminarDelCarrito(self, fila):
        """
        Elimina un producto del carrito
        """
        del self.carrito[fila]
        self.actualizarTablaCarrito()
        self.actualizarTotales()
        
    def limpiarCarrito(self):
        """
        Limpia todos los productos del carrito
        """
        if not self.carrito:
            return
            
        respuesta = QMessageBox.question(
            self,
            "Limpiar Carrito",
            "¿Está seguro que desea limpiar el carrito?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.carrito = []
            self.tabla_carrito.setRowCount(0)
            self.actualizarTotales()
        
    def actualizarTotales(self):
        """
        Actualiza los valores de subtotal, descuento y total
        """
        self.subtotal_venta = 0.0
        self.descuento_total = 0.0
        
        for item in self.carrito:
            subtotal_item = item['precio'] * item['cantidad']
            descuento_item = subtotal_item * (item['descuento'] / 100)
            
            self.subtotal_venta += subtotal_item
            self.descuento_total += descuento_item
        
        self.total_venta = self.subtotal_venta - self.descuento_total
        
        self.label_subtotal.setText(f"Subtotal: ${self.subtotal_venta:.2f}")
        self.label_descuento.setText(f"Descuento: -${self.descuento_total:.2f}")
        self.label_total.setText(f"TOTAL: ${self.total_venta:.2f}")
        
    def registrarClienteRapido(self):
        """
        Abre diálogo rápido para registrar cliente
        """
        QMessageBox.information(self, "Registro Rápido", 
                            "Funcionalidad de registro rápido de cliente")
        
    def confirmarVenta(self):
        """
        Confirma y registra la venta
        """
        if not self.carrito:
            QMessageBox.warning(self, "Carrito Vacío", 
                            "No hay productos en el carrito")
            return
        
        # Mostrar diálogo de confirmación
        metodo = self.combo_metodo_pago.currentText()
        cliente = self.combo_cliente.currentText()
        
        mensaje = f"""
        <h3>Confirmar Venta</h3>
        <p><b>Cliente:</b> {cliente}</p>
        <p><b>Método de Pago:</b> {metodo}</p>
        <p><b>Subtotal:</b> ${self.subtotal_venta:.2f}</p>
        <p><b>Descuento:</b> ${self.descuento_total:.2f}</p>
        <p><b>TOTAL:</b> ${self.total_venta:.2f}</p>
        """
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Venta",
            mensaje,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            # Aquí iría la lógica para guardar en la base de datos
            QMessageBox.information(self, "Venta Exitosa", 
                                f"Venta registrada correctamente\nTotal: ${self.total_venta:.2f}")
            self.limpiarCarrito()

# ============================================================================
# VISTA DE INVENTARIO
# ============================================================================

class InventarioView(QWidget):
    def __init__(self):
        """
        Inicializa la vista de inventario
        """
        super().__init__()
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz de inventario
        """
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("📦 Gestión de Inventario")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout_principal.addWidget(titulo)
        
        # Barra de herramientas
        toolbar = self.crearToolbar()
        layout_principal.addLayout(toolbar)
        
        # Filtros
        panel_filtros = self.crearPanelFiltros()
        layout_principal.addWidget(panel_filtros)
        
        # Tabla de productos
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(8)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "Código", "Producto", "Categoría", "Precio", 
            "Stock", "Stock Mínimo", "Estado", "Acciones"
        ])
        self.tabla_inventario.horizontalHeader().setStretchLastSection(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.NoEditTriggers)
        layout_principal.addWidget(self.tabla_inventario)
        
        # Cargar datos
        self.cargarInventario()
        
    def crearToolbar(self):
        """
        Crea la barra de herramientas con botones de acción
        """
        layout = QHBoxLayout()
        
        boton_agregar = QPushButton("➕ Agregar Producto")
        boton_agregar.setStyleSheet("background-color: #2ecc71;")
        boton_agregar.clicked.connect(self.agregarProducto)
        layout.addWidget(boton_agregar)
        
        boton_entrada = QPushButton("📥 Registrar Entrada")
        boton_entrada.clicked.connect(self.registrarEntrada)
        layout.addWidget(boton_entrada)
        
        boton_ajustar = QPushButton("⚙️ Ajustar Stock")
        boton_ajustar.clicked.connect(self.ajustarStock)
        layout.addWidget(boton_ajustar)
        
        boton_alertas = QPushButton("⚠️ Ver Alertas")
        boton_alertas.setStyleSheet("background-color: #e67e22;")
        boton_alertas.clicked.connect(self.verAlertas)
        layout.addWidget(boton_alertas)
        
        layout.addStretch()
        
        return layout
    
    def crearPanelFiltros(self):
        """
        Crea el panel de filtros de búsqueda
        """
        grupo = QGroupBox("Filtros de Búsqueda")
        layout = QHBoxLayout()
        grupo.setLayout(layout)
        
        # Búsqueda por texto
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar producto...")
        self.input_busqueda.textChanged.connect(self.aplicarFiltros)
        layout.addWidget(self.input_busqueda)
        
        # Filtro por categoría
        label_categoria = QLabel("Categoría:")
        layout.addWidget(label_categoria)
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "Todas", "Camisetas", "Pantalones", 
            "Ropa de Invierno", "Accesorios"
        ])
        self.combo_categoria.currentTextChanged.connect(self.aplicarFiltros)
        layout.addWidget(self.combo_categoria)
        
        # Filtro por estado
        label_estado = QLabel("Estado:")
        layout.addWidget(label_estado)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Normal", "Stock Bajo", "Sin Stock"])
        self.combo_estado.currentTextChanged.connect(self.aplicarFiltros)
        layout.addWidget(self.combo_estado)
        
        # Botón limpiar filtros
        boton_limpiar = QPushButton("🔄 Limpiar Filtros")
        boton_limpiar.clicked.connect(self.limpiarFiltros)
        layout.addWidget(boton_limpiar)
        
        return grupo
    
    def cargarInventario(self):
        """
        Carga los productos desde la base de datos
        """
        productos_ejemplo = [
            ("P001", "Camiseta Básica", "Camisetas", 150.00, 25, 10, "Normal"),
            ("P002", "Pantalón Jean", "Pantalones", 450.00, 15, 5, "Normal"),
            ("P003", "Sudadera Invernal", "Ropa de Invierno", 350.00, 3, 5, "Stock Bajo"),
            ("P004", "Gorra Deportiva", "Accesorios", 120.00, 30, 10, "Normal"),
            ("P005", "Playera Estampada", "Camisetas", 180.00, 0, 10, "Sin Stock"),
        ]
        
        self.tabla_inventario.setRowCount(len(productos_ejemplo))
        
        for fila, producto in enumerate(productos_ejemplo):
            for columna, valor in enumerate(producto):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear según estado
                if columna == 6:  # Columna Estado
                    if valor == "Stock Bajo":
                        item.setBackground(Qt.yellow)
                    elif valor == "Sin Stock":
                        item.setBackground(Qt.red)
                        item.setForeground(Qt.white)
                
                self.tabla_inventario.setItem(fila, columna, item)
            
            # Botones de acciones
            widget_acciones = QWidget()
            layout_acciones = QHBoxLayout()
            layout_acciones.setContentsMargins(2, 2, 2, 2)
            widget_acciones.setLayout(layout_acciones)
            
            boton_editar = QPushButton("✏️")
            boton_editar.setMaximumWidth(35)
            boton_editar.clicked.connect(lambda checked, f=fila: self.editarProducto(f))
            layout_acciones.addWidget(boton_editar)
            
            boton_ver = QPushButton("👁️")
            boton_ver.setMaximumWidth(35)
            boton_ver.clicked.connect(lambda checked, f=fila: self.verDetalleProducto(f))
            layout_acciones.addWidget(boton_ver)
            
            self.tabla_inventario.setCellWidget(fila, 7, widget_acciones)
    
    def agregarProducto(self):
        """
        Abre el diálogo para agregar un nuevo producto
        """
        dialogo = DialogoProducto(self)
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtenerDatos()
            QMessageBox.information(self, "Producto Agregado", 
                                f"Producto '{datos['nombre']}' agregado correctamente")
            self.cargarInventario()
            
    def editarProducto(self, fila):
        """
        Edita el producto seleccionado
        """
        codigo = self.tabla_inventario.item(fila, 0).text()
        QMessageBox.information(self, "Editar Producto", 
                            f"Editar producto {codigo}")
        
    def verDetalleProducto(self, fila):
        """
        Muestra el detalle completo del producto
        """
        codigo = self.tabla_inventario.item(fila, 0).text()
        nombre = self.tabla_inventario.item(fila, 1).text()
        categoria = self.tabla_inventario.item(fila, 2).text()
        precio = self.tabla_inventario.item(fila, 3).text()
        stock = self.tabla_inventario.item(fila, 4).text()
        
        detalle = f"""
        <h2>{nombre}</h2>
        <p><b>Código:</b> {codigo}</p>
        <p><b>Categoría:</b> {categoria}</p>
        <p><b>Precio:</b> ${precio}</p>
        <p><b>Stock:</b> {stock} unidades</p>
        """
        
        QMessageBox.information(self, "Detalle del Producto", detalle)
        
    def registrarEntrada(self):
        """
        Registra entrada de mercancía de proveedor
        """
        dialogo = DialogoEntradaMercancia(self)
        if dialogo.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Entrada Registrada", 
                                "Entrada de mercancía registrada correctamente")
            self.cargarInventario()
        
    def ajustarStock(self):
        """
        Permite ajustar manualmente el stock
        """
        fila_seleccionada = self.tabla_inventario.currentRow()
        
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Seleccione Producto", 
                            "Debe seleccionar un producto para ajustar su stock")
            return
        
        dialogo = DialogoAjusteStock(self)
        if dialogo.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Stock Ajustado", 
                                "Stock ajustado correctamente")
            self.cargarInventario()
        
    def verAlertas(self):
        """
        Muestra productos con stock bajo
        """
        mensaje = "<h3>Productos con Stock Bajo</h3><ul>"
        
        for fila in range(self.tabla_inventario.rowCount()):
            estado = self.tabla_inventario.item(fila, 6).text()
            if estado in ["Stock Bajo", "Sin Stock"]:
                nombre = self.tabla_inventario.item(fila, 1).text()
                stock = self.tabla_inventario.item(fila, 4).text()
                mensaje += f"<li><b>{nombre}</b>: {stock} unidades</li>"
        
        mensaje += "</ul>"
        
        QMessageBox.warning(self, "Alertas de Inventario", mensaje)
        
    def aplicarFiltros(self):
        """
        Aplica los filtros seleccionados
        """
        termino_busqueda = self.input_busqueda.text().lower()
        categoria_filtro = self.combo_categoria.currentText()
        estado_filtro = self.combo_estado.currentText()
        
        for fila in range(self.tabla_inventario.rowCount()):
            mostrar = True
            
            # Filtro de búsqueda
            if termino_busqueda:
                nombre = self.tabla_inventario.item(fila, 1).text().lower()
                codigo = self.tabla_inventario.item(fila, 0).text().lower()
                if termino_busqueda not in nombre and termino_busqueda not in codigo:
                    mostrar = False
            
            # Filtro de categoría
            if categoria_filtro != "Todas":
                categoria = self.tabla_inventario.item(fila, 2).text()
                if categoria != categoria_filtro:
                    mostrar = False
            
            # Filtro de estado
            if estado_filtro != "Todos":
                estado = self.tabla_inventario.item(fila, 6).text()
                if estado != estado_filtro:
                    mostrar = False
            
            self.tabla_inventario.setRowHidden(fila, not mostrar)
    
    def limpiarFiltros(self):
        """
        Limpia todos los filtros aplicados
        """
        self.input_busqueda.clear()
        self.combo_categoria.setCurrentIndex(0)
        self.combo_estado.setCurrentIndex(0)
        
        for fila in range(self.tabla_inventario.rowCount()):
            self.tabla_inventario.setRowHidden(fila, False)

# ============================================================================
# VISTA DE CLIENTES
# ============================================================================

class ClientesView(QWidget):
    def __init__(self):
        """
        Inicializa la vista de clientes
        """
        super().__init__()
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz de clientes
        """
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("👥 Gestión de Clientes")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout_principal.addWidget(titulo)
        
        # Barra de herramientas
        toolbar = self.crearToolbar()
        layout_principal.addLayout(toolbar)
        
        # Búsqueda
        panel_busqueda = self.crearPanelBusqueda()
        layout_principal.addWidget(panel_busqueda)
        
        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(6)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "ID", "Nombre", "Teléfono", "Email", "Total Compras", "Acciones"
        ])
        self.tabla_clientes.horizontalHeader().setStretchLastSection(True)
        self.tabla_clientes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_clientes.setEditTriggers(QTableWidget.NoEditTriggers)
        layout_principal.addWidget(self.tabla_clientes)
        
        # Cargar clientes
        self.cargarClientes()
        
    def crearToolbar(self):
        """
        Crea la barra de herramientas
        """
        layout = QHBoxLayout()
        
        boton_agregar = QPushButton("➕ Registrar Cliente")
        boton_agregar.setStyleSheet("background-color: #2ecc71;")
        boton_agregar.clicked.connect(self.registrarCliente)
        layout.addWidget(boton_agregar)
        
        layout.addStretch()
        
        return layout
    
    def crearPanelBusqueda(self):
        """
        Crea el panel de búsqueda
        """
        grupo = QGroupBox("Búsqueda de Clientes")
        layout = QHBoxLayout()
        grupo.setLayout(layout)
        
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre, teléfono o email...")
        self.input_busqueda.textChanged.connect(self.buscarCliente)
        layout.addWidget(self.input_busqueda)
        
        boton_limpiar = QPushButton("🔄 Limpiar")
        boton_limpiar.clicked.connect(self.limpiarBusqueda)
        layout.addWidget(boton_limpiar)
        
        return grupo
    
    def cargarClientes(self):
        """
        Carga la lista de clientes
        """
        clientes_ejemplo = [
            ("C001", "Juan Pérez", "333-123-4567", "juan@email.com", "$5,450.00"),
            ("C002", "María López", "333-234-5678", "maria@email.com", "$3,200.00"),
            ("C003", "Carlos Ruiz", "333-345-6789", "carlos@email.com", "$8,900.00"),
        ]
        
        self.tabla_clientes.setRowCount(len(clientes_ejemplo))
        
        for fila, cliente in enumerate(clientes_ejemplo):
            for columna, valor in enumerate(cliente):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_clientes.setItem(fila, columna, item)
            
            # Botones de acciones
            widget_acciones = QWidget()
            layout_acciones = QHBoxLayout()
            layout_acciones.setContentsMargins(2, 2, 2, 2)
            widget_acciones.setLayout(layout_acciones)
            
            boton_historial = QPushButton("📋 Historial")
            boton_historial.clicked.connect(lambda checked, f=fila: self.verHistorial(f))
            layout_acciones.addWidget(boton_historial)
            
            boton_editar = QPushButton("✏️")
            boton_editar.setMaximumWidth(35)
            boton_editar.clicked.connect(lambda checked, f=fila: self.editarCliente(f))
            layout_acciones.addWidget(boton_editar)
            
            self.tabla_clientes.setCellWidget(fila, 5, widget_acciones)
    
    def registrarCliente(self):
        """
        Abre el diálogo para registrar un nuevo cliente
        """
        dialogo = DialogoCliente(self)
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtenerDatos()
            QMessageBox.information(self, "Cliente Registrado", 
                                f"Cliente '{datos['nombre']}' registrado correctamente")
            self.cargarClientes()
    
    def verHistorial(self, fila):
        """
        Muestra el historial de compras del cliente seleccionado
        """
        nombre = self.tabla_clientes.item(fila, 1).text()
        
        historial = f"""
        <h2>Historial de Compras</h2>
        <h3>{nombre}</h3>
        <table border="1" cellpadding="5">
        <tr><th>Fecha</th><th>Total</th><th>Productos</th></tr>
        <tr><td>2024-11-15</td><td>$450.00</td><td>3</td></tr>
        <tr><td>2024-11-20</td><td>$780.00</td><td>5</td></tr>
        <tr><td>2024-11-28</td><td>$320.00</td><td>2</td></tr>
        </table>
        """
        
        QMessageBox.information(self, "Historial de Compras", historial)
    
    def editarCliente(self, fila):
        """
        Edita la información del cliente
        """
        id_cliente = self.tabla_clientes.item(fila, 0).text()
        QMessageBox.information(self, "Editar Cliente", 
                               f"Editar cliente {id_cliente}")
    
    def buscarCliente(self):
        """
        Busca clientes por nombre o teléfono
        """
        termino_busqueda = self.input_busqueda.text().lower()
        
        for fila in range(self.tabla_clientes.rowCount()):
            nombre = self.tabla_clientes.item(fila, 1).text().lower()
            telefono = self.tabla_clientes.item(fila, 2).text().lower()
            email = self.tabla_clientes.item(fila, 3).text().lower()
            
            if (termino_busqueda in nombre or 
                termino_busqueda in telefono or 
                termino_busqueda in email):
                self.tabla_clientes.setRowHidden(fila, False)
            else:
                self.tabla_clientes.setRowHidden(fila, True)
    
    def limpiarBusqueda(self):
        """
        Limpia el campo de búsqueda
        """
        self.input_busqueda.clear()
        for fila in range(self.tabla_clientes.rowCount()):
            self.tabla_clientes.setRowHidden(fila, False)

# ============================================================================
# VISTA DE PROVEEDORES
# ============================================================================

class ProveedoresView(QWidget):
    def __init__(self):
        """
        Inicializa la vista de proveedores
        """
        super().__init__()
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz de proveedores
        """
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("🚚 Gestión de Proveedores")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout_principal.addWidget(titulo)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        boton_agregar = QPushButton("➕ Registrar Proveedor")
        boton_agregar.setStyleSheet("background-color: #2ecc71;")
        boton_agregar.clicked.connect(self.registrarProveedor)
        toolbar.addWidget(boton_agregar)
        
        toolbar.addStretch()
        layout_principal.addLayout(toolbar)
        
        # Tabla de proveedores
        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(5)
        self.tabla_proveedores.setHorizontalHeaderLabels([
            "ID", "Nombre", "Contacto", "Teléfono", "Productos"
        ])
        self.tabla_proveedores.horizontalHeader().setStretchLastSection(True)
        layout_principal.addWidget(self.tabla_proveedores)
        
        # Cargar datos
        self.cargarProveedores()
    
    def cargarProveedores(self):
        """
        Carga la lista de proveedores
        """
        proveedores_ejemplo = [
            ("PR001", "Textiles del Norte", "Pedro García", "333-111-2222", "15"),
            ("PR002", "Moda Express", "Ana Martínez", "333-222-3333", "23"),
            ("PR003", "Distribuidora Fashion", "Luis Torres", "333-333-4444", "18"),
        ]
        
        self.tabla_proveedores.setRowCount(len(proveedores_ejemplo))
        
        for fila, proveedor in enumerate(proveedores_ejemplo):
            for columna, valor in enumerate(proveedor):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_proveedores.setItem(fila, columna, item)
    
    def registrarProveedor(self):
        """
        Registra un nuevo proveedor
        """
        dialogo = DialogoProveedor(self)
        if dialogo.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Proveedor Registrado", 
                                "Proveedor registrado correctamente")
            self.cargarProveedores()

# ============================================================================
# VISTA DE REPORTES
# ============================================================================

class ReportesView(QWidget):
    def __init__(self):
        """
        Inicializa la vista de reportes
        """
        super().__init__()
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura los elementos de la interfaz de reportes
        """
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("📊 Reportes y Estadísticas")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout_principal.addWidget(titulo)
        
        # Panel de opciones
        panel_opciones = self.crearPanelOpciones()
        layout_principal.addWidget(panel_opciones)
        
        # Área de visualización
        self.area_visualizacion = QTextEdit()
        self.area_visualizacion.setReadOnly(True)
        layout_principal.addWidget(self.area_visualizacion)
        
        # Mostrar reporte inicial
        self.generarReporteVentas()
    
    def crearPanelOpciones(self):
        """
        Crea el panel con opciones de reportes
        """
        grupo = QGroupBox("Tipo de Reporte")
        layout = QVBoxLayout()
        grupo.setLayout(layout)
        
        # Filtros de fecha
        layout_fechas = QHBoxLayout()
        
        label_desde = QLabel("Desde:")
        layout_fechas.addWidget(label_desde)
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.setCalendarPopup(True)
        layout_fechas.addWidget(self.fecha_desde)
        
        label_hasta = QLabel("Hasta:")
        layout_fechas.addWidget(label_hasta)
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        layout_fechas.addWidget(self.fecha_hasta)
        
        layout.addLayout(layout_fechas)
        
        # Botones de reportes
        layout_botones = QHBoxLayout()
        
        boton_ventas = QPushButton("💰 Ventas")
        boton_ventas.clicked.connect(self.generarReporteVentas)
        layout_botones.addWidget(boton_ventas)
        
        boton_inventario = QPushButton("📦 Inventario")
        boton_inventario.clicked.connect(self.generarReporteInventario)
        layout_botones.addWidget(boton_inventario)
        
        boton_productos = QPushButton("🏆 Productos Top")
        boton_productos.clicked.connect(self.generarReporteProductosTop)
        layout_botones.addWidget(boton_productos)
        
        boton_exportar = QPushButton("📄 Exportar")
        boton_exportar.setStyleSheet("background-color: #27ae60;")
        boton_exportar.clicked.connect(self.exportarReporte)
        layout_botones.addWidget(boton_exportar)
        
        layout.addLayout(layout_botones)
        
        return grupo
    
    def generarReporteVentas(self):
        """
        Genera el reporte de ventas
        """
        reporte = f"""
        <h2>Reporte de Ventas</h2>
        <p><b>Período:</b> {self.fecha_desde.date().toString('dd/MM/yyyy')} - 
        {self.fecha_hasta.date().toString('dd/MM/yyyy')}</p>
        
        <h3>Resumen</h3>
        <table border="1" cellpadding="8" style="width:100%;">
        <tr style="background-color:#34495e; color:white;">
            <th>Concepto</th>
            <th>Valor</th>
        </tr>
        <tr>
            <td>Total de Ventas</td>
            <td style="text-align:right;"><b>$45,890.00</b></td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Número de Transacciones</td>
            <td style="text-align:right;">128</td>
        </tr>
        <tr>
            <td>Ticket Promedio</td>
            <td style="text-align:right;">$358.52</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Productos Vendidos</td>
            <td style="text-align:right;">342</td>
        </tr>
        </table>
        
        <h3>Ventas por Método de Pago</h3>
        <table border="1" cellpadding="8" style="width:100%;">
        <tr style="background-color:#34495e; color:white;">
            <th>Método</th>
            <th>Monto</th>
            <th>Porcentaje</th>
        </tr>
        <tr>
            <td>Efectivo</td>
            <td style="text-align:right;">$18,356.00</td>
            <td style="text-align:right;">40%</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Tarjeta</td>
            <td style="text-align:right;">$22,945.00</td>
            <td style="text-align:right;">50%</td>
        </tr>
        <tr>
            <td>Transferencia</td>
            <td style="text-align:right;">$4,589.00</td>
            <td style="text-align:right;">10%</td>
        </tr>
        </table>
        """
        
        self.area_visualizacion.setHtml(reporte)
    
    def generarReporteInventario(self):
        """
        Genera el reporte de inventario
        """
        reporte = f"""
        <h2>Reporte de Inventario</h2>
        <p><b>Fecha:</b> {QDate.currentDate().toString('dd/MM/yyyy')}</p>
        
        <h3>Resumen General</h3>
        <table border="1" cellpadding="8" style="width:100%;">
        <tr style="background-color:#34495e; color:white;">
            <th>Concepto</th>
            <th>Valor</th>
        </tr>
        <tr>
            <td>Total de Productos</td>
            <td style="text-align:right;">245</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Valor del Inventario</td>
            <td style="text-align:right;"><b>$128,450.00</b></td>
        </tr>
        <tr>
            <td>Productos con Stock Bajo</td>
            <td style="text-align:right; color:orange;"><b>8</b></td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Productos Sin Stock</td>
            <td style="text-align:right; color:red;"><b>3</b></td>
        </tr>
        </table>
        
        <h3>Inventario por Categoría</h3>
        <table border="1" cellpadding="8" style="width:100%;">
        <tr style="background-color:#34495e; color:white;">
            <th>Categoría</th>
            <th>Productos</th>
            <th>Valor</th>
        </tr>
        <tr>
            <td>Camisetas</td>
            <td style="text-align:right;">85</td>
            <td style="text-align:right;">$38,250.00</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Pantalones</td>
            <td style="text-align:right;">62</td>
            <td style="text-align:right;">$45,890.00</td>
        </tr>
        <tr>
            <td>Ropa de Invierno</td>
            <td style="text-align:right;">48</td>
            <td style="text-align:right;">$32,100.00</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td>Accesorios</td>
            <td style="text-align:right;">50</td>
            <td style="text-align:right;">$12,210.00</td>
        </tr>
        </table>
        """
        
        self.area_visualizacion.setHtml(reporte)
    
    def generarReporteProductosTop(self):
        """
        Genera el reporte de productos más vendidos
        """
        reporte = f"""
        <h2>Productos Más Vendidos</h2>
        <p><b>Período:</b> {self.fecha_desde.date().toString('dd/MM/yyyy')} - 
        {self.fecha_hasta.date().toString('dd/MM/yyyy')}</p>
        
        <h3>Top 10 Productos</h3>
        <table border="1" cellpadding="8" style="width:100%;">
        <tr style="background-color:#34495e; color:white;">
            <th>#</th>
            <th>Producto</th>
            <th>Categoría</th>
            <th>Unidades</th>
            <th>Total Ventas</th>
        </tr>
        <tr style="background-color:#2ecc71; color:white;">
            <td style="text-align:center;">1</td>
            <td>Camiseta Básica</td>
            <td>Camisetas</td>
            <td style="text-align:right;">52</td>
            <td style="text-align:right;">$7,800.00</td>
        </tr>
        <tr style="background-color:#27ae60; color:white;">
            <td style="text-align:center;">2</td>
            <td>Pantalón Jean</td>
            <td>Pantalones</td>
            <td style="text-align:right;">45</td>
            <td style="text-align:right;">$20,250.00</td>
        </tr>
        <tr>
            <td style="text-align:center;">3</td>
            <td>Playera Estampada</td>
            <td>Camisetas</td>
            <td style="text-align:right;">38</td>
            <td style="text-align:right;">$6,840.00</td>
        </tr>
        <tr style="background-color:#ecf0f1;">
            <td style="text-align:center;">4</td>
            <td>Sudadera Invernal</td>
            <td>Ropa de Invierno</td>
            <td style="text-align:right;">32</td>
            <td style="text-align:right;">$11,200.00</td>
        </tr>
        <tr>
            <td style="text-align:center;">5</td>
            <td>Gorra Deportiva</td>
            <td>Accesorios</td>
            <td style="text-align:right;">28</td>
            <td style="text-align:right;">$3,360.00</td>
        </tr>
        </table>
        
        <h3>Productos con Baja Rotación</h3>
        <p style="color:orange;"><b>⚠️ Productos que no se han vendido en los últimos 30 días:</b></p>
        <ul>
        <li>Chamarra de Cuero - 15 unidades en stock</li>
        <li>Bufanda de Lana - 8 unidades en stock</li>
        <li>Guantes Térmicos - 12 unidades en stock</li>
        </ul>
        """
        
        self.area_visualizacion.setHtml(reporte)
    
    def exportarReporte(self):
        """
        Exporta el reporte a PDF o Excel
        """
        QMessageBox.information(self, "Exportar Reporte", 
                            "Funcionalidad de exportación (PDF/Excel)")

# ============================================================================
# DIÁLOGOS
# ============================================================================

class DialogoProducto(QDialog):
    def __init__(self, parent=None):
        """
        Diálogo para agregar/editar productos
        """
        super().__init__(parent)
        self.setWindowTitle("Nuevo Producto")
        self.setMinimumWidth(500)
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura el formulario de producto
        """
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Campos del formulario
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Generado automáticamente")
        self.input_codigo.setReadOnly(True)
        layout.addRow("Código:", self.input_codigo)
        
        self.input_nombre = QLineEdit()
        layout.addRow("* Nombre:", self.input_nombre)
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "Camisetas", "Pantalones", 
            "Ropa de Invierno", "Accesorios"
        ])
        layout.addRow("* Categoría:", self.combo_categoria)
        
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMaximum(999999.99)
        self.input_precio.setPrefix("$")
        layout.addRow("* Precio:", self.input_precio)
        
        self.input_stock = QSpinBox()
        self.input_stock.setMaximum(99999)
        layout.addRow("* Stock Inicial:", self.input_stock)
        
        self.input_stock_minimo = QSpinBox()
        self.input_stock_minimo.setMaximum(999)
        self.input_stock_minimo.setValue(5)
        layout.addRow("* Stock Mínimo:", self.input_stock_minimo)
        
        # Sección de variantes
        label_variantes = QLabel("Variantes (Tallas/Colores):")
        label_variantes.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addRow(label_variantes)
        
        self.check_variantes = QCheckBox("Este producto tiene variantes")
        layout.addRow(self.check_variantes)
        
        # Nota
        nota = QLabel("* Campos obligatorios")
        nota.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addRow(nota)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.validarYAceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
    
    def validarYAceptar(self):
        """
        Valida los datos antes de aceptar
        """
        if not self.input_nombre.text():
            QMessageBox.warning(self, "Campo Requerido", 
                            "Debe ingresar el nombre del producto")
            return
        
        if self.input_precio.value() <= 0:
            QMessageBox.warning(self, "Precio Inválido", 
                            "El precio debe ser mayor a cero")
            return
        
        self.accept()
    
    def obtenerDatos(self):
        """
        Retorna los datos del formulario
        """
        return {
            'nombre': self.input_nombre.text(),
            'categoria': self.combo_categoria.currentText(),
            'precio': self.input_precio.value(),
            'stock': self.input_stock.value(),
            'stock_minimo': self.input_stock_minimo.value()
        }

class DialogoCliente(QDialog):
    def __init__(self, parent=None):
        """
        Diálogo para registrar clientes
        """
        super().__init__(parent)
        self.setWindowTitle("Registrar Cliente")
        self.setMinimumWidth(450)
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura el formulario de cliente
        """
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Campos
        self.input_nombre = QLineEdit()
        layout.addRow("* Nombre Completo:", self.input_nombre)
        
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("333-XXX-XXXX")
        layout.addRow("* Teléfono:", self.input_telefono)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("ejemplo@email.com")
        layout.addRow("Email:", self.input_email)
        
        self.input_direccion = QLineEdit()
        layout.addRow("Dirección:", self.input_direccion)
        
        # Nota
        nota = QLabel("* Campos obligatorios")
        nota.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addRow(nota)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.validarYAceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
    
    def validarYAceptar(self):
        """
        Valida los datos antes de aceptar
        """
        if not self.input_nombre.text():
            QMessageBox.warning(self, "Campo Requerido", 
                            "Debe ingresar el nombre del cliente")
            return
        
        if not self.input_telefono.text():
            QMessageBox.warning(self, "Campo Requerido", 
                            "Debe ingresar el teléfono del cliente")
            return
        
        self.accept()
    
    def obtenerDatos(self):
        """
        Retorna los datos del formulario
        """
        return {
            'nombre': self.input_nombre.text(),
            'telefono': self.input_telefono.text(),
            'email': self.input_email.text(),
            'direccion': self.input_direccion.text()
        }

class DialogoProveedor(QDialog):
    def __init__(self, parent=None):
        """
        Diálogo para registrar proveedores
        """
        super().__init__(parent)
        self.setWindowTitle("Registrar Proveedor")
        self.setMinimumWidth(450)
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura el formulario de proveedor
        """
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.input_nombre = QLineEdit()
        layout.addRow("* Nombre Empresa:", self.input_nombre)
        
        self.input_contacto = QLineEdit()
        layout.addRow("* Persona Contacto:", self.input_contacto)
        
        self.input_telefono = QLineEdit()
        layout.addRow("* Teléfono:", self.input_telefono)
        
        self.input_email = QLineEdit()
        layout.addRow("Email:", self.input_email)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

class DialogoEntradaMercancia(QDialog):
    def __init__(self, parent=None):
        """
        Diálogo para registrar entrada de mercancía
        """
        super().__init__(parent)
        self.setWindowTitle("Registrar Entrada de Mercancía")
        self.setMinimumWidth(500)
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura el formulario de entrada
        """
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItems([
            "Textiles del Norte",
            "Moda Express",
            "Distribuidora Fashion"
        ])
        layout.addRow("* Proveedor:", self.combo_proveedor)
        
        self.combo_producto = QComboBox()
        self.combo_producto.addItems([
            "Camiseta Básica",
            "Pantalón Jean",
            "Sudadera Invernal"
        ])
        layout.addRow("* Producto:", self.combo_producto)
        
        self.input_cantidad = QSpinBox()
        self.input_cantidad.setMinimum(1)
        self.input_cantidad.setMaximum(9999)
        layout.addRow("* Cantidad:", self.input_cantidad)
        
        self.input_costo = QDoubleSpinBox()
        self.input_costo.setPrefix("$")
        self.input_costo.setMaximum(999999.99)
        layout.addRow("Costo Unitario:", self.input_costo)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

class DialogoAjusteStock(QDialog):
    def __init__(self, parent=None):
        """
        Diálogo para ajustar stock manualmente
        """
        super().__init__(parent)
        self.setWindowTitle("Ajustar Stock")
        self.setMinimumWidth(400)
        self.inicializarUI()
        
    def inicializarUI(self):
        """
        Configura el formulario de ajuste
        """
        layout = QFormLayout()
        self.setLayout(layout)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Agregar Stock",
            "Reducir Stock",
            "Establecer Cantidad Exacta"
        ])
        layout.addRow("* Tipo de Ajuste:", self.combo_tipo)
        
        self.input_cantidad = QSpinBox()
        self.input_cantidad.setMinimum(1)
        self.input_cantidad.setMaximum(9999)
        layout.addRow("* Cantidad:", self.input_cantidad)
        
        self.input_motivo = QTextEdit()
        self.input_motivo.setMaximumHeight(80)
        self.input_motivo.setPlaceholderText("Ej: Producto dañado, merma, inventario físico...")
        layout.addRow("* Motivo:", self.input_motivo)
        
        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.validarYAceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
    
    def validarYAceptar(self):
        """
        Valida que se haya ingresado un motivo
        """
        if not self.input_motivo.toPlainText().strip():
            QMessageBox.warning(self, "Motivo Requerido", 
                            "Debe ingresar el motivo del ajuste")
            return
        
        self.accept()

# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que inicia la aplicación
    """
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    ventana = MainWindow()
    ventana.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()