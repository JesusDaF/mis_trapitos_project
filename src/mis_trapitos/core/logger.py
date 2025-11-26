import logging
import os
from datetime import datetime

def configurarLogger():
    """
    Configura el sistema de logging para escribir errores tanto en consola
    como en un archivo de texto persistente.
    """
    # Nombre del archivo de log con fecha (opcional) o fijo. Usaremos fijo para rotación simple.
    nombre_archivo = "sistema_errores.log"
    
    # Formato del mensaje: [FECHA HORA] [NIVEL] Mensaje
    formato_log = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 1. Configuración del manejador de archivo (FileHandler)
    file_handler = logging.FileHandler(nombre_archivo, encoding='utf-8')
    file_handler.setLevel(logging.ERROR) # Solo guardamos errores o críticos en el archivo
    file_handler.setFormatter(formato_log)

    # 2. Configuración del manejador de consola (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG) # En consola vemos todo
    console_handler.setFormatter(formato_log)

    # 3. Configuración del logger raíz
    logger = logging.getLogger('MisTrapitosLogger')
    logger.setLevel(logging.DEBUG)
    
    # Evitamos duplicar handlers si la función se llama varias veces
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Instancia global lista para importar
log = configurarLogger()