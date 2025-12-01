import tkinter as tk
from tkinter import messagebox
from mis_trapitos.core.logger import log

#Importar vistas 
from mis_trapitos.ui.inventario_view import InventoryView
from mis_trapitos.ui.ventas_view import SalesView
from mis_trapitos.ui.clientes_view import CustomersView
from mis_trapitos.ui.reportes_view import ReportsView
from mis_trapitos.ui.usuarios_view import UsersView
from mis_trapitos.ui.proveedores_view import SuppliersView

class MainWindow(tk.Frame):
    """
    Contenedor principal de la aplicación.
    Gestiona el menú lateral y el cambio dinámico de vistas (Frames).
    """

    def __init__(self, root, usuario_sesion, cerrar_sesion_callback):
        """
        root: La ventana base de Tkinter (creada en app.py)
        usuario_sesion: Diccionario con datos del usuario logueado {'rol': 'admin', ...}
        cerrar_sesion_callback: Función para volver al Login
        """
        super().__init__(root)
        self.root = root
        self.usuario = usuario_sesion
        self.callback_logout = cerrar_sesion_callback
        
        self.pack(fill="both", expand=True)
        
        # Diccionario para guardar las instancias de las vistas y no recargarlas siempre
        self.vistas_cache = {} 
        
        # Configurar UI
        self._configurarEstilos()
        self._crearLayoutPrincipal()
        self._construirMenuLateral()
        
        # Cargar vista por defecto (Ventas)
        self.cambiarVista("Ventas")
        
        log.info(f"Ventana principal cargada para usuario: {self.usuario['nombre']}")

    def _configurarEstilos(self):
        """Configuraciones visuales básicas (colores, fuentes)"""
        self.color_menu = "#2C3E50" # Azul oscuro
        self.color_fondo = "#ECF0F1" # Gris claro
        self.estilo_boton = {"bg": "#34495E", "fg": "white", "font": ("Arial", 12), "bd": 0, "pady": 10}

    def _crearLayoutPrincipal(self):
        """Divide la ventana en 2: Menú (Izquierda) y Contenido (Derecha)"""
        # 1. Panel Lateral (Menú)
        self.frame_menu = tk.Frame(self, bg=self.color_menu, width=250)
        self.frame_menu.pack(side="left", fill="y")
        self.frame_menu.pack_propagate(False) # Evita que se encoja

        # 2. Panel de Contenido (Donde cambian las vistas)
        self.frame_contenido = tk.Frame(self, bg=self.color_fondo)
        self.frame_contenido.pack(side="right", fill="both", expand=True)
        
        # Header en el menú con nombre de usuario
        lbl_user = tk.Label(
            self.frame_menu, 
            text=f"Hola,\n{self.usuario['nombre']}", 
            bg=self.color_menu, 
            fg="#F1C40F", # Amarillo
            font=("Arial", 14, "bold"),
            pady=20
        )
        lbl_user.pack(side="top", fill="x")

    def _construirMenuLateral(self):
        """Crea los botones según el ROL del usuario"""
        rol = self.usuario['rol']
        
        # Lista de opciones: (Texto, ClaveVista, RequiereAdmin)
        opciones = [
            ("🛒 Punto de Venta", "Ventas", False),
            ("📦 Inventario", "Inventario", False), # Empleados pueden ver/editar stock básico
            ("👥 Clientes", "Clientes", False),
            ("🚚 Proveedores", "Proveedores", False),
        ]

        # Opciones exclusivas de Administrador
        if rol == 'admin':
            opciones.append(("📊 Reportes", "Reportes", True))
            opciones.append(("🔐 Usuarios", "Usuarios", True))

        # Generar Botones
        for texto, clave, es_admin in opciones:
            btn = tk.Button(
                self.frame_menu, 
                text=texto, 
                command=lambda v=clave: self.cambiarVista(v),
                **self.estilo_boton
            )
            btn.pack(fill="x", pady=2)

        # Botón Salir (Siempre al final)
        btn_salir = tk.Button(
            self.frame_menu,
            text="🚪 Cerrar Sesión",
            bg="#C0392B", # Rojo
            fg="white",
            font=("Arial", 12, "bold"),
            command=self._accionCerrarSesion
        )
        btn_salir.pack(side="bottom", fill="x", pady=20, padx=10)

    def cambiarVista(self, clave_vista):
        """
        Lógica para intercambiar los Frames en el área de contenido.
        """
        # 1. Limpiar contenido actual
        for widget in self.frame_contenido.winfo_children():
            widget.destroy() 
        
        # 2. Cargar la nueva vista
        # Aquí importamos las clases de las vistas
        frame_nuevo = None
        
        if clave_vista == "Ventas":
            frame_nuevo = SalesView(self.frame_contenido, self.usuario)
             
        elif clave_vista == "Inventario":
            frame_nuevo = InventoryView(self.frame_contenido, self.usuario)

        elif clave_vista == "Reportes":
            frame_nuevo = ReportsView(self.frame_contenido)
             

        elif clave_vista == "Clientes":
            frame_nuevo = CustomersView(self.frame_contenido, self.usuario)

        elif clave_vista == "Usuarios":
            frame_nuevo = UsersView(self.frame_contenido, self.usuario) 

        elif clave_vista == "Proveedores":
            frame_nuevo = SuppliersView(self.frame_contenido, self.usuario)

        if frame_nuevo:
            frame_nuevo.pack(fill="both", expand=True)

    def _accionCerrarSesion(self):
        if messagebox.askyesno("Salir", "¿Cerrar sesión actual?"):
            self.callback_logout()