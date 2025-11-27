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

# Ejecutamos la configuración antes de importar nada de 'mis_trapitos'
configurarEntorno()

# Ahora podemos importar nuestra aplicación
from mis_trapitos.app import MisTrapitosApp

if __name__ == "__main__":
    # Instanciamos la aplicación principal
    app = MisTrapitosApp()
    
    # Arrancamos el sistema
    # (Si la BD falló en el __init__, la ventana no se abrirá)
    try:
        if hasattr(app, 'root'): # Verificamos que se haya creado correctamente
            app.iniciarAplicacion()
    except KeyboardInterrupt:
        print("Aplicación interrumpida por el usuario.")