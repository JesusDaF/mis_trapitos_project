import tkinter as tk
from tkinter import messagebox
from mis_trapitos.core.logger import log
from mis_trapitos.database_conexion.db_manager import DBManager

class MisTrapitosApp:
    """
    Clase principal que inicializa la aplicación gráfica (GUI) y el entorno.
    Actúa como el contenedor raíz (Root) de Tkinter.
    """

    def __init__(self):
        """Configura la ventana base y verifica dependencias"""
        # 1. Inicializamos el sistema de logs (Ya se hace al importar, pero registramos el inicio)
        log.info("--- Iniciando sistema Mis Trapitos ---")

        # 2. Configuración de la Ventana Principal (Root)
        self.root = tk.Tk()
        self.root.title("Mis Trapitos - Gestión de Tienda")
        # Definimos un tamaño por defecto (Ancho x Alto)
        self.root.geometry("1024x768")
        # Color de fondo base (opcional)
        self.root.configure(bg="#f0f0f0")

        # 3. Verificación de Salud del Sistema (Base de Datos)
        if not self._verificarConexionBaseDatos():
            # Si falla la BD, mostramos error y cerramos, no tiene caso seguir.
            self.root.destroy()
            return

        # 4. Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.cerrarAplicacion)

        # AQUI INICIALIZAREMOS LAS VISTAS (LOGIN / MAIN) MÁS ADELANTE
        # Por ahora, dejamos un placeholder visual
        self._cargarVistaInicial()

    def _verificarConexionBaseDatos(self):
        """
        Método privado para asegurar que PostgreSQL responde antes de abrir la ventana.
        """
        db = DBManager()
        conn = db.obtenerConexion()
        
        if conn:
            log.info("Verificación de inicio: Conexión a BD exitosa.")
            db.cerrarConexion(conn)
            return True
        else:
            log.critical("Verificación de inicio: FALLO conexión a BD.")
            messagebox.showerror(
                "Error Crítico", 
                "No se pudo conectar a la base de datos local.\n\n"
                "Verifique que PostgreSQL esté ejecutándose y que el archivo .env sea correcto."
            )
            return False

    def _cargarVistaInicial(self):
        """
        Determina qué pantalla mostrar al arrancar
        Aquí se mostrará el Login, pero por ahora mostramos un mensaje de bienvenida
        """
        # Etiqueta temporal para verificar que la app corre
        label_bienvenida = tk.Label(
            self.root, 
            text="Sistema Mis Trapitos\nListo para cargar interfaces", 
            font=("Arial", 20),
            bg="#f0f0f0",
            fg="#333"
        )
        label_bienvenida.pack(expand=True)

    def iniciarAplicacion(self):
        """Arranca el bucle principal de la interfaz gráfica (Main Loop)"""
        if self.root:
            try:
                log.info("Interfaz gráfica mostrada al usuario.")
                self.root.mainloop()
            except Exception as e:
                log.error(f"Error fatal en la interfaz gráfica: {e}")

    def cerrarAplicacion(self):
        """Maneja el cierre ordenado del software"""
        if messagebox.askokcancel("Salir", "¿Desea cerrar el sistema?"):
            log.info("--- Sistema cerrado por el usuario ---")
            self.root.destroy()