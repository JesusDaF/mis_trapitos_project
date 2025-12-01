## Controlador de autenticación

import hashlib
from mis_trapitos.database_conexion.queries import UsuariosQueries
from mis_trapitos.core.logger import log

class AuthController:
    """
    Controlador encargado de la lógica de autenticación y seguridad.
    Gestiona el inicio de sesión y el hashing de contraseñas con registro de auditoría.
    """

    def __init__(self):
        """Inicializa la capa de consultas de usuarios"""
        self.queries = UsuariosQueries()
        self.usuario_actual = None # Almacena la sesión del usuario logueado

    def _generarHash(self, contrasena_texto):
        """
        Método privado para encriptar la contraseña usando SHA-256
        """
        # Convertimos texto a bytes y luego generamos el hash hexadecimal
        return hashlib.sha256(contrasena_texto.encode()).hexdigest()

    def iniciarSesion(self, usuario, contrasena):
        """
        Verifica las credenciales del usuario.
        Retorna una tupla: (True, DatosUsuario) si es exitoso, (False, MensajeError) si falla.
        """
        try:
            # 1. Buscamos al usuario en la BD
            datos_usuario = self.queries.obtenerUsuarioPorUser(usuario)
            
            if not datos_usuario:
                # Log de advertencia: Usuario no encontrado
                log.warning(f"Intento de login fallido: Usuario '{usuario}' no existe o inactivo.")
                return False, "El usuario no existe o está inactivo."

            # datos_usuario = (id_empleado, nombre, hash_contrasena, rol)
            hash_almacenado = datos_usuario[2]
            
            # 2. Verificamos la contraseña
            hash_ingresado = self._generarHash(contrasena)
            
            if hash_ingresado == hash_almacenado:
                # Guardamos la sesión en memoria
                self.usuario_actual = {
                    'id': datos_usuario[0],
                    'nombre': datos_usuario[1],
                    'rol': datos_usuario[3]
                }
                # Log de éxito (Auditoría)
                log.info(f"Sesión iniciada exitosamente: Usuario '{usuario}' (ID: {datos_usuario[0]}).")
                return True, "Inicio de sesión exitoso."
                
            else:
                # Log de advertencia: Contraseña incorrecta (Seguridad)
                log.warning(f"Intento de login fallido: Contraseña incorrecta para usuario '{usuario}'.")
                return False, "Contraseña incorrecta."

        except Exception as e:
            log.error(f"Error crítico durante el inicio de sesión de '{usuario}': {e}")
            return False, "Error del sistema al intentar iniciar sesión."

    def cerrarSesion(self):
        """Limpia la sesión actual"""
        if self.usuario_actual:
            log.info(f"Cierre de sesión: Usuario '{self.usuario_actual.get('nombre')}' (ID: {self.usuario_actual.get('id')}).")
        
        self.usuario_actual = None

    def registrarEmpleado(self, nombre, usuario, contrasena, rol, usuario_admin_actual):
        """
        Crea un nuevo empleado. Incluye validación de permisos (solo admin puede crear).
        """
        # 1. Validación de permisos (Seguridad)
        if not usuario_admin_actual or usuario_admin_actual['rol'] != 'admin':
            solicitante = usuario_admin_actual.get('nombre', 'Desconocido') if usuario_admin_actual else 'Anonimo'
            log.warning(f"ACCESO DENEGADO: Intento de crear usuario por '{solicitante}' sin privilegios de admin.")
            return False, "Permiso denegado: Solo administradores pueden registrar empleados."
        
        # 2. Validación de datos
        if len(contrasena) < 4:
            return False, "La contraseña es muy corta (mínimo 4 caracteres)."

        try:
            hash_pass = self._generarHash(contrasena)
            
            nuevo_id = self.queries.crearEmpleado(nombre, usuario, hash_pass, rol)
            
            if nuevo_id:
                # --- NUEVO: AUDITORÍA EN BD ---
                # Registramos quién creó al empleado
                self.queries.registrarLog(
                    id_empleado=usuario_admin_actual['id'], 
                    accion="REGISTRO EMPLEADO", 
                    descripcion=f"Se creó el usuario '{usuario}' con rol '{rol}'."
                )
                
                log.info(f"Nuevo empleado registrado: '{usuario}' (ID: {nuevo_id}).")
                return True, f"Empleado registrado con ID {nuevo_id}"
            else:
                log.error(f"Fallo al registrar empleado '{usuario}'.")
                return False, "Error al registrar (posiblemente ya existe)."

        except Exception as e:
            log.error(f"Excepción al registrar empleado '{usuario}': {e}")
            return False, f"Error del sistema: {e}"
    
    # METODO PUENTE    
    
    def obtenerListaEmpleados(self):
        """Retorna todos los usuarios registrados."""
        try:
            return self.queries.obtenerTodosLosUsuarios()
        except Exception as e:
            log.error(f"Error al listar empleados: {e}")
            return []
        
    def eliminarEmpleado(self, id_admin, id_empleado_a_eliminar):
        """Elimina un usuario, evitando que se elimine a sí mismo."""
        if id_admin == id_empleado_a_eliminar:
            return False, "No puedes eliminar tu propia cuenta mientras estás logueado."

        try:
            filas = self.queries.eliminarUsuario(id_empleado_a_eliminar)
            if filas:
                # Logueamos la acción usando queries internos 
                self.queries.registrarLog(id_admin, "BAJA USUARIO", f"Se eliminó al empleado ID {id_empleado_a_eliminar}")
                return True, "Usuario eliminado del sistema."
            else:
                return False, "Usuario no encontrado."
        except Exception as e:
            log.error(f"Error eliminando usuario: {e}")
            if "foreign key" in str(e).lower():
                return False, "No se puede eliminar: El usuario tiene ventas o registros históricos."
            return False, f"Error: {e}"