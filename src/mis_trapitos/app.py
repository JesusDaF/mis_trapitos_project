import tkinter as tk
from tkinter import messagebox
from mis_trapitos.core.logger import log
from mis_trapitos.database_conexion.db_manager import DBManager

# Importamos las vistas
from mis_trapitos.ui.login_view import LoginView
from mis_trapitos.ui.main_window import MainWindow 


class MisTrapitosApp:
    """
    Clase principal que inicializa la aplicación gráfica.
    Gestiona el ciclo de vida: Login <-> Ventana Principal.
    """

    def __init__(self):
        """Configura la ventana base y verifica dependencias"""
        log.info("--- Iniciando sistema Mis Trapitos ---")

        # Configuración Root
        self.root = tk.Tk()
        self.root.title("Mis Trapitos - Gestión de Tienda")
        self.root.geometry("1024x768")
        self.root.state('zoomed') # Iniciar maximizado (funciona en Windows)
        
        # Verificación BD
        if not self._verificarConexionBaseDatos():
            self.root.destroy()
            return

        self.root.protocol("WM_DELETE_WINDOW", self.cerrarAplicacion)
        
        # Variable para almacenar la vista actual
        self.vista_actual = None

        # Iniciamos mostrando el Login
        self.mostrarLogin()

    def _verificarConexionBaseDatos(self):
        db = DBManager()
        conn = db.obtenerConexion()
        if conn:
            db.cerrarConexion(conn)
            return True
        else:
            log.critical("Fallo conexión inicial BD")
            messagebox.showerror("Error Crítico", "No se pudo conectar a la base de datos.")
            return False

    def mostrarLogin(self):
        """Destruye la vista actual y carga el Login"""
        if self.vista_actual:
            self.vista_actual.destroy()
        
        self.root.title("Mis Trapitos - Acceso")
        # Instanciamos la vista de Login y le pasamos la función para cuando tenga éxito
        self.vista_actual = LoginView(self.root, self.alIngresarCorrectamente)

    def mostrarMenuPrincipal(self, usuario_data):
        """Destruye el Login y carga el Dashboard Principal"""
        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.root.title(f"Mis Trapitos - Sesión de: {usuario_data['nombre']}")
        
        # Instanciamos la ventana principal
        # Le pasamos los datos del usuario y la función para cerrar sesión
        self.vista_actual = MainWindow(self.root, usuario_data, self.alCerrarSesion)

    # --- CALLBACKS (Puentes entre vistas) ---

    def alIngresarCorrectamente(self, datos_usuario):
        """Se ejecuta cuando el LoginView valida al usuario"""
        self.mostrarMenuPrincipal(datos_usuario)

    def alCerrarSesion(self):
        """Se ejecuta cuando el usuario presiona 'Salir' en MainWindow"""
        self.mostrarLogin()

    def iniciarAplicacion(self):
        if self.root:
            self.root.mainloop()

    def cerrarAplicacion(self):
        if messagebox.askokcancel("Salir", "¿Desea cerrar el sistema?"):
            self.root.destroy()