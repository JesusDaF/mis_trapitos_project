import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from mis_trapitos.core.logger import log

load_dotenv()

class DBManager:
    """Clase responsable de gestionar la conexión con la base de datos PostgreSQL"""

    def __init__(self):
        """Inicializa los parámetros de conexión cargados desde el archivo .env"""
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.port = os.getenv('DB_PORT')

    def obtenerConexion(self):
        """Establece conexión con la BD y retorna el objeto conexión"""
        try:
            conexion_bd = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return conexion_bd
        except Error as error_detectado:
            log.error(f"Fallo crítico de conexión a BD: {error_detectado}")
            return None

    def cerrarConexion(self, conexion_activa):
        """Cierra la conexión activa si existe para liberar recursos"""
        if conexion_activa:
            conexion_activa.close()

    def ejecutarConsulta(self, query_sql, parametros=None, conexion_externa=None):
        """
        Ejecuta INSERT/UPDATE/DELETE.
        Si recibe 'conexion_externa', NO hace commit ni cierra (parte de una transacción).
        Si NO recibe 'conexion_externa', crea una nueva, hace commit y cierra (operación simple).
        """
        # Si nos pasan una conexión, la usamos. Si no, creamos una nueva.
        conn = conexion_externa if conexion_externa else self.obtenerConexion()
        usar_conexion_externa = conexion_externa is not None
        registros_afectados = 0

        if conn:
            try:
                cursor = conn.cursor()
                if parametros:
                    cursor.execute(query_sql, parametros)
                else:
                    cursor.execute(query_sql)
                
                registros_afectados = cursor.rowcount
                
                # SOLO hacemos commit si la conexión es nuestra (no externa)
                if not usar_conexion_externa:
                    conn.commit()
                    # print("Consulta ejecutada y guardada (Auto-commit)")

            except Error as e:
                log.error(f"Error SQL en ejecutarConsulta: {e} | Query: {query_sql}")
                # Si es conexión externa, el error debe propagarse para que el controlador haga rollback
                if usar_conexion_externa:
                    raise e 
                return None
            finally:
                if cursor:
                    cursor.close()
                # SOLO cerramos si la conexión es nuestra
                if not usar_conexion_externa:
                    self.cerrarConexion(conn)
        
        return registros_afectados

    def ejecutarInsertReturning(self, query_sql, parametros=None, conexion_externa=None):
        """
        Ejecuta INSERT con RETURNING (para obtener IDs).
        Soporta transacciones externas.
        """
        conn = conexion_externa if conexion_externa else self.obtenerConexion()
        usar_conexion_externa = conexion_externa is not None
        resultado = None

        if conn:
            try:
                cursor = conn.cursor()
                if parametros:
                    cursor.execute(query_sql, parametros)
                else:
                    cursor.execute(query_sql)
                
                resultado = cursor.fetchone()
                
                if not usar_conexion_externa:
                    conn.commit()

            except Error as e:
                log.error(f"Error SQL en ejecutarInsertReturning: {e} | Query: {query_sql}")
                if usar_conexion_externa:
                    raise e
            finally:
                if cursor:
                    cursor.close()
                if not usar_conexion_externa:
                    self.cerrarConexion(conn)
        
        return resultado

    def obtenerDatos(self, query_sql, parametros=None, conexion_externa=None):
        """Ejecuta SELECT y retorna resultados. Soporta conexión externa."""
        conn = conexion_externa if conexion_externa else self.obtenerConexion()
        usar_conexion_externa = conexion_externa is not None
        resultados = []

        if conn:
            try:
                cursor = conn.cursor()
                if parametros:
                    cursor.execute(query_sql, parametros)
                else:
                    cursor.execute(query_sql)
                
                resultados = cursor.fetchall()
            except Error as e:
                log.error(f"Error SQL en obtenerDatos: {e}")
                if usar_conexion_externa:
                    raise e
            finally:
                if cursor:
                    cursor.close()
                if not usar_conexion_externa:
                    self.cerrarConexion(conn)
        
        return resultados