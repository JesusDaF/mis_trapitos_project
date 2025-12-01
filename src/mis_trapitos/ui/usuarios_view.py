import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from mis_trapitos.logica.auth_control import AuthController

class UsersView(tk.Frame):
    """
    Vista de Gestión de Usuarios 
    Solo accesible por Administradores. Permite registrar nuevos empleados.
    """

    def __init__(self, parent, usuario_admin_sesion):
        super().__init__(parent)
        self.usuario_admin = usuario_admin_sesion
        self.controller = AuthController()
        
        self._crearInterfaz()
        self.cargarDatosTabla()

    def _crearInterfaz(self):
        #  BARRA DE HERRAMIENTAS 
        frame_toolbar = tk.Frame(self, bg="white", pady=10, padx=10)
        frame_toolbar.pack(fill="x")

        tk.Button(
            frame_toolbar, text="👤 Nuevo Usuario", 
            bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalNuevo
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_toolbar, text="🔄 Actualizar Lista", 
            bg="#7F8C8D", fg="white", font=("Segoe UI", 10),
            command=self.cargarDatosTabla
        ).pack(side="left", padx=5)

        # TABLA DE USUARIOS
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "nombre", "usuario", "rol", "estado")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre Completo")
        self.tree.heading("usuario", text="Usuario (Login)")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("estado", text="Activo")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("usuario", width=100)
        self.tree.column("rol", width=100, anchor="center")
        self.tree.column("estado", width=60, anchor="center")

        self.tree.pack(fill="both", expand=True)

    def cargarDatosTabla(self):
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        datos = self.controller.obtenerListaEmpleados()
        for row in datos:
            # row = (id, nombre, usuario, rol, activo)
            # Convertir booleano a texto
            fila_visual = list(row)
            fila_visual[4] = "Sí" if row[4] else "No"
            
            self.tree.insert("", "end", values=fila_visual)

    def _abrirModalNuevo(self):
        VentanaAltaUsuario(self)

# VENTANA MODAL: ALTA USUARIO 
class VentanaAltaUsuario(Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.view = parent_view
        self.title("Nuevo Usuario del Sistema")
        self.geometry("400x450")
        self.configure(bg="white")
        self.transient(parent_view)
        self.grab_set()
        
        self._construirFormulario()

    def _construirFormulario(self):
        tk.Label(self, text="Registrar Empleado", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(self, bg="white", padx=30)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Nombre Completo:", bg="white").pack(anchor="w")
        self.entry_nom = tk.Entry(frame, font=("Segoe UI", 10))
        self.entry_nom.pack(fill="x", pady=(0, 10))
        
        tk.Label(frame, text="Usuario (Para Login):", bg="white").pack(anchor="w")
        self.entry_user = tk.Entry(frame, font=("Segoe UI", 10))
        self.entry_user.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Contraseña:", bg="white").pack(anchor="w")
        self.entry_pass = tk.Entry(frame, font=("Segoe UI", 10), show="*") # Ocultar caracteres
        self.entry_pass.pack(fill="x", pady=(0, 10))
        
        tk.Label(frame, text="Rol / Permisos:", bg="white").pack(anchor="w")
        self.combo_rol = ttk.Combobox(frame, values=["empleado", "admin"], state="readonly", font=("Segoe UI", 10))
        self.combo_rol.current(0) # Default: empleado
        self.combo_rol.pack(fill="x", pady=(0, 20))

        tk.Button(
            self, text="CREAR USUARIO", 
            bg="#2C3E50", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=30, pady=20)

    def _guardar(self):
        nom = self.entry_nom.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        rol = self.combo_rol.get()
        
        if not nom or not user or not pwd:
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return

        # Llamada al controlador (hash y logs)
        exito, msg = self.view.controller.registrarEmpleado(
            nom, user, pwd, rol, 
            self.view.usuario_admin # Pasamos quien esta creando al usuario para el LOG
        )
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.view.cargarDatosTabla()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)