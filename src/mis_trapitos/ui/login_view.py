import tkinter as tk
from tkinter import messagebox
from mis_trapitos.logica.auth_control import AuthController
from mis_trapitos.core.logger import log

class LoginView(tk.Frame):
    """
    Vista de inicio de sesión.
    Responsabilidad: Capturar credenciales y validar acceso.
    """

    def __init__(self, parent_container, on_login_success_callback):
        """
        parent_container: Widget padre (root o frame)
        on_login_success_callback: Función de app.py a ejecutar si el login es correcto
                                   (recibe los datos del usuario).
        """
        super().__init__(parent_container)
        self.configure(bg="#2C3E50") # Fondo oscuro 
        self.callback_exito = on_login_success_callback
        
        self.auth_controller = AuthController()
        
        self.pack(fill="both", expand=True)
        
        self._construirInterfaz()

    def _construirInterfaz(self):
        """Dibuja el formulario centrado en la pantalla"""
        
        # Frame central (Tarjeta blanca)
        frame_card = tk.Frame(self, bg="white", padx=40, pady=40)
        frame_card.place(relx=0.5, rely=0.5, anchor="center")
        
        # 1. Título / Logo
        lbl_titulo = tk.Label(
            frame_card, 
            text="MIS TRAPITOS", 
            font=("Helvetica", 24, "bold"), 
            bg="white", 
            fg="#2C3E50"
        )
        lbl_titulo.pack(pady=(0, 10))
        
        lbl_subtitulo = tk.Label(
            frame_card, 
            text="Acceso al Sistema", 
            font=("Arial", 12), 
            bg="white", 
            fg="#7F8C8D"
        )
        lbl_subtitulo.pack(pady=(0, 30))

        # 2. Campo Usuario
        tk.Label(frame_card, text="Usuario:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        self.entry_user = tk.Entry(frame_card, font=("Arial", 12), width=25)
        self.entry_user.pack(pady=(5, 15))
        self.entry_user.focus() # Poner el cursor aquí al iniciar

        # 3. Campo Contraseña
        tk.Label(frame_card, text="Contraseña:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        self.entry_pass = tk.Entry(frame_card, font=("Arial", 12), width=25, show="*")
        self.entry_pass.pack(pady=(5, 20))
        
        # Permitir login con tecla Enter
        self.entry_pass.bind('<Return>', lambda event: self._accionLogin())

        # 4. Botón Entrar
        btn_entrar = tk.Button(
            frame_card, 
            text="INICIAR SESIÓN", 
            bg="#27AE60", # Verde
            fg="white", 
            font=("Arial", 11, "bold"),
            width=20,
            pady=5,
            command=self._accionLogin
        )
        btn_entrar.pack()

    def _accionLogin(self):
        """Maneja el evento del botón"""
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor ingrese usuario y contraseña.")
            return

        # Llamada a la Lógica de Negocio
        exito, resultado = self.auth_controller.iniciarSesion(usuario, password)
        
        if exito:
            # resultado contiene los datos del usuario (dict)
            log.info(f"Login exitoso desde UI: {usuario}")
            # Llamamos al callback de app.py para cambiar de pantalla
            self.callback_exito(self.auth_controller.usuario_actual)
        else:
            messagebox.showerror("Error de Acceso", resultado)
            self.entry_pass.delete(0, tk.END) # Limpiar contraseña