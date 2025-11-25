import sys
import os

# Ajuste de ruta para que Python encuentre el paquete 'src' desde la raíz
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mis_trapitos.database_conexion.db_manager import DBManager

def ejecutarPruebaConexion():
    """Instancia el gestor de BD e intenta establecer una conexión para verificar credenciales"""
    
    gestor_db = DBManager() # instancia encargada de la comunicación con la BD
    
    print("--- Iniciando Test de Conexión ---")
    
    conexion_activa = gestor_db.obtenerConexion() # objeto de conexión si es exitoso, o None si falla
    
    if conexion_activa:
        print("¡ÉXITO! La conexión a la base de datos se estableció correctamente.")
        
        # Bloque extra para verificar que realmente podemos pedir datos al servidor
        try:
            cursor_prueba = conexion_activa.cursor() # cursor para ejecutar la consulta de versión
            cursor_prueba.execute("SELECT version();")
            
            version_servidor = cursor_prueba.fetchone() # tupla con la información de la versión
            
            if version_servidor:
                print(f"Respuesta del servidor: {version_servidor[0]}")
            
            cursor_prueba.close()
            
        except Exception as error_consulta:
            print(f"Conectó, pero hubo un error al consultar versión: {error_consulta}")
            
        # Siempre cerramos la conexión al finalizar
        gestor_db.cerrarConexion(conexion_activa)
        
    else:
        print("FALLO: No se pudo conectar.")
        print("   -> Verifica que el archivo .env tenga los datos correctos.")
        print("   -> Asegúrate de que PostgreSQL esté ejecutándose.")

if __name__ == "__main__":
    ejecutarPruebaConexion()