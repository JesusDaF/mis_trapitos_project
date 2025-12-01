import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from mis_trapitos.logica.producto_control import ProductController

class SuppliersView(tk.Frame):
    """
    Vista de Gestión de Proveedores 
    Permite registrar y visualizar la lista de proveedores para reposición.
    """

    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        # Usamos ProductController porque ahí pusimos la lógica de proveedores
        self.controller = ProductController()
        
        self._crearInterfaz()
        self.cargarDatosTabla()

    def _crearInterfaz(self):
        # --- BARRA DE HERRAMIENTAS ---
        frame_toolbar = tk.Frame(self, bg="white", pady=10, padx=10)
        frame_toolbar.pack(fill="x")

        tk.Button(
            frame_toolbar, text="🚚 Nuevo Proveedor", 
            bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalNuevo
        ).pack(side="left", padx=5)
        
        tk.Button(
            frame_toolbar, text="🔄 Actualizar Lista", 
            bg="#7F8C8D", fg="white", font=("Segoe UI", 10),
            command=self.cargarDatosTabla
        ).pack(side="left", padx=5)

        tk.Button(
            frame_toolbar, text="🗑️ Eliminar", bg="#C0392B", fg="white", font=("Segoe UI", 10),
            command=self._accionEliminar
        ).pack(side="left", padx=5)

        # --- TABLA DE DATOS ---
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "nombre", "contacto")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre del Proveedor")
        self.tree.heading("contacto", text="Datos de Contacto")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=250)
        self.tree.column("contacto", width=400)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargarDatosTabla(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obtener datos desde el controlador
        datos = self.controller.obtenerListaProveedores()
        
        for row in datos:
            # row = (id, nombre, contacto)
            self.tree.insert("", "end", values=row)

    def _abrirModalNuevo(self):
        VentanaAltaProveedor(self)

    def _accionEliminar(self):
        seleccion = self.tree.selection()
        if not seleccion: return
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar este proveedor?\nSe desvinculará de los productos asociados"): return

        id_prov = self.tree.item(seleccion[0])['values'][0]
        
        exito, msg = self.controller.eliminarProveedor(self.usuario['id'], id_prov)
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargarDatosTabla()
        else:
            messagebox.showerror("Error", msg)

# VENTANA MODAL: ALTA PROVEEDOR 
class VentanaAltaProveedor(Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.view = parent_view
        self.title("Registrar Proveedor")
        self.geometry("400x300")
        self.configure(bg="white")
        self.transient(parent_view)
        self.grab_set()
        
        self._construirFormulario()

    def _construirFormulario(self):
        tk.Label(self, text="Nuevo Proveedor", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(self, bg="white", padx=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Nombre Empresa / Proveedor *:", bg="white").pack(anchor="w")
        self.entry_nom = tk.Entry(frame, font=("Segoe UI", 10))
        self.entry_nom.pack(fill="x", pady=(0, 10))
        
        tk.Label(frame, text="Datos de Contacto (Tel / Dirección / Email):", bg="white").pack(anchor="w")
        self.entry_cont = tk.Entry(frame, font=("Segoe UI", 10))
        self.entry_cont.pack(fill="x", pady=(0, 10))

        tk.Button(
            self, text="GUARDAR PROVEEDOR", 
            bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold"),
            pady=10, command=self._guardar
        ).pack(fill="x", padx=20, pady=20)


    def _guardar(self):
        nom = self.entry_nom.get().strip()
        contacto = self.entry_cont.get().strip()
        
        if not nom:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return

        # Llamada al controlador
        exito, msg = self.view.controller.registrarProveedor(
            self.view.usuario['id'], # ID empleado para el Log
            nom, 
            contacto
        )
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.view.cargarDatosTabla()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)