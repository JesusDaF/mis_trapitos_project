import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from mis_trapitos.logica.cliente_control import CustomerController

class CustomersView(tk.Frame):
    """
    Vista de Gestión de Clientes (RF-1.3).
    Permite registrar clientes y visualizar su historial de compras.
    """

    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.usuario = usuario_data
        self.controller = CustomerController()
        
        self._crearInterfaz()
        self.cargarDatosTabla()

    def _crearInterfaz(self):
        # BARRA SUPERIOR 
        frame_toolbar = tk.Frame(self, bg="white", pady=10, padx=10)
        frame_toolbar.pack(fill="x")

        tk.Button(
            frame_toolbar, text="+ Nuevo Cliente", 
            bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
            command=self._abrirModalNuevo
        ).pack(side="left", padx=5)

        tk.Button(
            frame_toolbar, text="📜 Ver Historial de Compras", 
            bg="#2980B9", fg="white", font=("Segoe UI", 10),
            command=self._verHistorial
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

        # TABLA DE DATOS 
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "nombre", "telefono", "email", "direccion")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre Completo")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("email", text="Email")
        self.tree.heading("direccion", text="Dirección")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("telefono", width=100, anchor="center")
        self.tree.column("email", width=150)
        self.tree.column("direccion", width=200)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargarDatosTabla(self):
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        datos = self.controller.obtenerListaClientes()
        for row in datos:
            self.tree.insert("", "end", values=row)

    # ACCIONES 

    def _abrirModalNuevo(self):
        VentanaAltaCliente(self)

    def _verHistorial(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente para ver su historial.")
            return
            
        item = self.tree.item(seleccion[0])
        id_cliente = item['values'][0]
        nombre_cliente = item['values'][1]
        
        # Obtener historial desde el controlador
        historial = self.controller.obtenerHistorialCompras(id_cliente)
        
        VentanaHistorial(self, nombre_cliente, historial)

    def _accionEliminar(self):
        seleccion = self.tree.selection()
        if not seleccion: return
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar este cliente de la base de datos?"): return

        id_cliente = self.tree.item(seleccion[0])['values'][0]
        
        exito, msg = self.controller.eliminarCliente(self.usuario['id'], id_cliente)
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargarDatosTabla()
        else:
            messagebox.showerror("Error", msg)

# VENTANA MODAL: ALTA CLIENTE
class VentanaAltaCliente(Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.view = parent_view
        self.title("Nuevo Cliente")
        self.geometry("400x350")
        self.configure(bg="white")
        self.transient(parent_view)
        self.grab_set()
        
        self._construirFormulario()

    def _construirFormulario(self):
        tk.Label(self, text="Registrar Cliente", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=10)
        
        frame = tk.Frame(self, bg="white", padx=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Nombre Completo *:", bg="white").pack(anchor="w")
        self.entry_nom = tk.Entry(frame); self.entry_nom.pack(fill="x", pady=5)
        
        tk.Label(frame, text="Teléfono *:", bg="white").pack(anchor="w")
        self.entry_tel = tk.Entry(frame); self.entry_tel.pack(fill="x", pady=5)

        tk.Label(frame, text="Email:", bg="white").pack(anchor="w")
        self.entry_email = tk.Entry(frame); self.entry_email.pack(fill="x", pady=5)
        
        tk.Label(frame, text="Dirección:", bg="white").pack(anchor="w")
        self.entry_dir = tk.Entry(frame); self.entry_dir.pack(fill="x", pady=5)

        tk.Button(self, text="GUARDAR", bg="#27AE60", fg="white", command=self._guardar).pack(fill="x", padx=20, pady=20)

    def _guardar(self):
        nom = self.entry_nom.get()
        tel = self.entry_tel.get()
        email = self.entry_email.get()
        dire = self.entry_dir.get()
        
        # El controlador maneja logs y validaciones
        exito, msg = self.view.controller.registrarNuevoCliente(
            self.view.usuario['id'], nom, dire, email, tel
        )
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.view.cargarDatosTabla()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

# VENTANA MODAL: HISTORIAL 
class VentanaHistorial(Toplevel):
    def __init__(self, parent, nombre_cliente, datos_historial):
        super().__init__(parent)
        self.title(f"Historial: {nombre_cliente}")
        self.geometry("500x400")
        
        tk.Label(self, text=f"Compras de {nombre_cliente}", font=("Segoe UI", 12, "bold"), pady=10).pack()
        
        # Tabla simple
        cols = ("fecha", "total", "items")
        tree = ttk.Treeview(self, columns=cols, show="headings")
        tree.heading("fecha", text="Fecha")
        tree.heading("total", text="Total ($)")
        tree.heading("items", text="Artículos")
        
        tree.column("fecha", width=150)
        tree.column("total", width=100, anchor="e")
        tree.column("items", width=80, anchor="center")
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not datos_historial:
            tk.Label(self, text="Este cliente aún no tiene compras registradas.", fg="gray").pack()
        else:
            for row in datos_historial:
                # row = (fecha, monto, items)
                # Formatear fecha
                fecha_fmt = row[0].strftime("%d/%m/%Y %H:%M")
                monto_fmt = f"${row[1]:.2f}"
                tree.insert("", "end", values=(fecha_fmt, monto_fmt, row[2]))