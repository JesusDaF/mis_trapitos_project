## Controlador de clientes

from mis_trapitos.database_conexion.queries import ClientesQueries, UsuariosQueries
from mis_trapitos.core.logger import log

class CustomerController:
    """
    Controlador encargado de la lógica de negocio relacionada con los Clientes.
    """

    def __init__(self):
        """Inicializa las consultas de clientes y usuarios (para logs)"""
        self.client_queries = ClientesQueries()
        self.usr_queries = UsuariosQueries()

    def registrarNuevoCliente(self, id_empleado, nombre, direccion, email, telefono):
        """
        Valida y registra un nuevo cliente en la base de datos.
        """
        # 1. Validaciones
        if not nombre or len(nombre.strip()) == 0:
            return False, "El nombre del cliente es obligatorio."
        
        if not telefono or len(telefono.strip()) == 0:
            return False, "El teléfono es obligatorio (se usa para buscarlo en caja)."

        # Opcional: Validación básica de email
        if email and "@" not in email:
            return False, "El formato del correo electrónico no parece válido."

        try:
            # 2. Intentar guardar
            # Limpiamos espacios en blanco extra
            id_cliente = self.client_queries.registrarCliente(
                nombre.strip(), 
                direccion.strip() if direccion else "", 
                email.strip() if email else "", 
                telefono.strip()
            )
            
            if id_cliente:
                # 3. Auditoría
                self.usr_queries.registrarLog(
                    id_empleado,
                    "ALTA CLIENTE",
                    f"Nuevo cliente registrado: '{nombre}' (Tel: {telefono})."
                )
                
                log.info(f"Cliente registrado: {nombre} (ID: {id_cliente})")
                return True, f"Cliente registrado exitosamente con ID {id_cliente}"
            else:
                # Posiblemente el teléfono o email ya existen (UNIQUE constraints)
                log.warning(f"Fallo al registrar cliente '{nombre}'. Posible duplicado.")
                return False, "Error: No se pudo registrar (verifique si el teléfono o email ya existen)."

        except Exception as e:
            log.error(f"Error al registrar cliente: {e}")
            return False, f"Error del sistema: {e}"

    def buscarClientePorTelefono(self, telefono):
        """
        Busca un cliente para seleccionarlo rápidamente durante una venta.
        Retorna: Diccionario con datos o None.
        """
        try:
            if not telefono: return None
            
            # datos = (id_cliente, nombre, direccion) según queries.py
            datos = self.client_queries.buscarClientePorTelefono(telefono)
            
            if datos:
                return {
                    'id': datos[0],
                    'nombre': datos[1],
                    'direccion': datos[2]
                }
            return None
        except Exception as e:
            log.error(f"Error buscando cliente por tel {telefono}: {e}")
            return None

    def obtenerHistorialCompras(self, id_cliente):
        """
        Obtiene la lista de compras realizadas por un cliente (RF-1.3).
        """
        try:
            if not id_cliente: return []
            return self.client_queries.obtenerHistorialCliente(id_cliente)
        except Exception as e:
            log.error(f"Error obteniendo historial de cliente {id_cliente}: {e}")
            return []