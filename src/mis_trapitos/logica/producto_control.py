## Controlador de productos

from datetime import datetime
from mis_trapitos.database_conexion.queries import InventarioQueries, ProveedoresQueries, UsuariosQueries
from mis_trapitos.core.logger import log

class ProductController:
    """
    Controlador para la gestión de catálogo de productos, categorías y proveedores
    Aplica reglas de validación antes de guardar
    """

    def __init__(self):
        self.inv_queries = InventarioQueries()
        self.prov_queries = ProveedoresQueries()
        self.usr_queries = UsuariosQueries()

    def crearNuevaCategoria(self, id_empleado, nombre, descripcion): 
        """Valida y crea una categoría, registrando el log"""
        if not nombre or len(nombre.strip()) == 0:
            return False, "Nombre obligatorio."
        
        try:
            exito = self.inv_queries.crearCategoria(nombre.strip(), descripcion)
            if exito:
                # --- AUDITORÍA ---
                self.usr_queries.registrarLog(
                    id_empleado, 
                    "CREAR CATEGORIA", 
                    f"Nueva categoría: {nombre}"
                )
                log.info(f"Nueva categoría creada: '{nombre}'")
                return True, "Categoría creada exitosamente."
            else:
                log.error(f"Fallo al crear categoría '{nombre}' (Posible duplicado).")
                return False, "Error al crear categoría (quizás ya existe)."
        except Exception as e:
            log.error(f"Excepción al crear categoría '{nombre}': {e}")
            return False, f"Error del sistema: {e}"

    def registrarProductoNuevo(self, id_empleado,id_categoria, descripcion, precio, lista_variantes):
        """
        Registra un producto completo con sus variantes iniciales de forma atómica.
        Si falla cualquier parte del proceso, no se guarda nada en la BD.
        """
        # 1. VALIDACIONES PREVIAS 
        
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                return False, "El precio debe ser mayor a 0."
        except ValueError:
            return False, "El precio debe ser un número válido."

        if not descripcion:
            return False, "La descripción del producto es obligatoria."
        
        if not lista_variantes or len(lista_variantes) == 0:
            return False, "Debe agregar al menos una variante (talla/color) al producto."

        # 2. INICIO DE LA TRANSACCIÓN 
        # Abrimos conexión manual para controlar el Commit/Rollback
        conn = self.inv_queries.db.obtenerConexion()
        if not conn:
            log.critical("No hay conexión a BD para registrar producto.")
            return False, "Error de conexión."
        
        try:
            log.info(f"Iniciando registro de producto: '{descripcion}' con {len(lista_variantes)} variantes.")
            # Crear Producto Padre (Pasando la conexión)
            # Ahora sí, precio_float está definido y validado
            id_prod = self.inv_queries.crearProducto(
                id_categoria, descripcion, precio_float, conexion_externa=conn
            )
            
            if not id_prod:
                raise Exception("No se pudo crear el encabezado del producto")

            # Crear Variantes (Pasando la conexión)
            contador_variantes = 0
            for variante in lista_variantes:
                stock = int(variante['stock'])
                # Ignoramos variantes con stock negativo, pero no rompemos el ciclo
                if stock < 0: continue 
                
                self.inv_queries.crearVarianteProducto(
                    id_prod, 
                    variante['talla'], 
                    variante['color'], 
                    stock,
                    conexion_externa=conn
                )
                contador_variantes += 1
            
            if contador_variantes == 0:
                 raise Exception("No se registraron variantes válidas (revise el stock)")

            self.usr_queries.registrarLog(
                id_empleado=id_empleado,
                accion="ALTA PRODUCTO",
                descripcion=f"Producto '{descripcion}' creado con {len(lista_variantes)} variantes.",
                conexion_externa=conn
            )

            # Guardamos cambios.
            conn.commit()
            log.info(f"Producto '{descripcion}' (ID: {id_prod}) registrado correctamente.")
            return True, f"Producto creado con {contador_variantes} variantes."

        except Exception as e:
            # Si algo falló, deshacemos 
            if conn:
                conn.rollback()
            log.error(f"Transacción de producto fallida: {e}")
            return False, f"Error al guardar producto: {str(e)}"
            
        finally:
            # cerramos la conexión al terminar
            if conn:
                self.inv_queries.db.cerrarConexion(conn)

    def obtenerCatalogo(self):
        # Aquí para transformar los datos si la UI necesita un formato especial JSON/Dict
        
        """Retorna la lista de productos formateada para la vista."""
        try:
            return self.inv_queries.obtenerProductosEnInventario()
        except Exception as e:
            log.error(f"Error al obtener el catálogo de productos: {e}")
            return []
        

    def agregarOferta(self, id_producto, porcentaje, fecha_inicio_str, fecha_fin_str):
        """
        Crea una oferta para un producto (RF 1.1).
        Valida que el porcentaje sea correcto y que la fecha fin sea posterior a la de inicio.
        Fechas deben venir en formato 'YYYY-MM-DD'.
        """
        # 1. Validar Porcentaje
        try:
            porc = float(porcentaje)
            if porc <= 0 or porc > 100:
                return False, "El porcentaje debe estar entre 1% y 100%."
        except ValueError:
            return False, "El porcentaje debe ser un número."

        # 2. Validar Fechas
        try:
            f_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            f_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

            if f_fin < f_inicio:
                return False, "La fecha de fin no puede ser anterior a la de inicio."
            
            if f_fin < datetime.now().date():
                 return False, "No puedes crear una oferta que ya expiró."

        except ValueError:
            return False, "Formato de fecha inválido. Use AAAA-MM-DD."

        # 3. Guardar
        from mis_trapitos.database_conexion.queries import DescuentosQueries
        desc_queries = DescuentosQueries() # Instancia local para no ensuciar el init principal
        
        exito = desc_queries.registrarDescuento(id_producto, porc, f_inicio, f_fin)
        
        if exito:
            log.info(f"Oferta del {porc}% agregada al producto ID {id_producto}.")
            return True, f"Oferta del {porc}% registrada correctamente."
        return False, "Error al guardar la oferta." 
    
    def registrarProveedor(self, id_empleado, nombre, contacto):
        """
        Registra un nuevo proveedor en el sistema.
        """
        if not nombre or len(nombre.strip()) == 0:
            return False, "El nombre del proveedor es obligatorio."

        try:
            # 1. Intentamos crear el proveedor
            id_prov = self.prov_queries.registrarProveedor(nombre.strip(), contacto)
            
            if id_prov:
                # 2. Auditoría
                self.usr_queries.registrarLog(
                    id_empleado,
                    "ALTA PROVEEDOR",
                    f"Nuevo proveedor registrado: '{nombre}'."
                )
                log.info(f"Proveedor registrado: {nombre} (ID: {id_prov})")
                return True, f"Proveedor '{nombre}' registrado correctamente."
            else:
                log.error(f"Error al registrar proveedor '{nombre}'.")
                return False, "Error al guardar el proveedor."

        except Exception as e:
            log.error(f"Excepción en registrarProveedor: {e}")
            return False, f"Error del sistema: {e}"

    def obtenerListaProveedores(self):
        """
        Retorna la lista de todos los proveedores para mostrarlos en la UI.
        """
        try:
            return self.prov_queries.obtenerProveedores()
        except Exception as e:
            log.error(f"Error al obtener lista de proveedores: {e}")
            return []

    def vincularProductoAProveedor(self, id_empleado, id_proveedor, id_producto):
        """
        Asocia un producto existente a un proveedor para reposición.
        """
        try:
            # Validamos que ambos IDs existan (básico)
            if not id_proveedor or not id_producto:
                return False, "Datos incompletos para la vinculación."

            exito = self.prov_queries.asociarProductoProveedor(id_proveedor, id_producto)
            
            if exito:
                # Auditoría
                self.usr_queries.registrarLog(
                    id_empleado,
                    "VINCULAR PROVEEDOR",
                    f"Se asoció el proveedor ID {id_proveedor} al producto ID {id_producto}."
                )
                log.info(f"Vínculo creado: Prov {id_proveedor} -> Prod {id_producto}")
                return True, "Producto asociado al proveedor correctamente."
            else:
                # Esto pasa si ya estaba vinculado (Primary Key compuesta duplicada)
                log.warning(f"Intento duplicado de vincular Prov {id_proveedor} con Prod {id_producto}")
                return False, "Este producto ya está asociado a ese proveedor."

        except Exception as e:
            log.error(f"Error al vincular proveedor: {e}")
            return False, f"Error del sistema: {e}"

    def obtenerProveedoresDeProducto(self, id_producto):
        """
        Obtiene qué proveedores surten un producto específico (para reportes o reposición).
        """
        try:
            return self.prov_queries.obtenerProveedoresDeProducto(id_producto)
        except Exception as e:
            log.error(f"Error al obtener proveedores del producto {id_producto}: {e}")
            return []