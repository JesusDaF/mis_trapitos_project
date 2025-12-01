import sys
import os

def configurarEntorno():
    """
    Asegura que Python pueda encontrar los módulos dentro de la carpeta 'src'.
    Esto permite ejecutar main.py desde cualquier ubicación sin errores de importación.
    """
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_src = os.path.join(ruta_base, 'src')
    
    if ruta_src not in sys.path:
        sys.path.insert(0, ruta_src)

# Ejecutamos la configuración antes de importar 
configurarEntorno()

# Ahora a importar la aplicación
from mis_trapitos.app import MisTrapitosApp

if __name__ == "__main__":
    # Instanciamos la aplicación principal
    app = MisTrapitosApp()
    
    # Arrancamos el sistema
    
    try:
        if hasattr(app, 'root'): # Verificamos que se haya creado correctamente
            app.iniciarAplicacion()
    except KeyboardInterrupt:
        print("Aplicación interrumpida por el usuario.")