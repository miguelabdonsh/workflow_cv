import os
from pathlib import Path

def get_script_path(script_name: str) -> str:
    """
    Obtiene la ruta absoluta a un script basado en la estructura del proyecto.
    
    Args:
        script_name: Nombre del script (ej: 'cv_microservice.py')
        
    Returns:
        Ruta absoluta al script
    """
    # Obtener el directorio actual
    current_dir = Path(__file__).resolve().parent
    
    # Calcular directorio raíz del backend
    backend_dir = current_dir.parent.parent
    
    # Construir ruta al script
    if script_name.startswith('app/'):
        # Si ya incluye el prefijo app/
        script_path = os.path.join(backend_dir, script_name)
    else:
        # Si solo es el nombre del script, asumimos que está en services
        script_path = os.path.join(backend_dir, 'app', 'services', script_name)
    
    return str(script_path)

def get_project_root() -> Path:
    """
    Obtiene la ruta absoluta al directorio raíz del proyecto
    
    Returns:
        Path al directorio raíz
    """
    current_dir = Path(__file__).resolve().parent
    return current_dir.parent.parent 