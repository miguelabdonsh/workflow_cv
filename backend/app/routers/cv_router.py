from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json
import subprocess
import tempfile
import uuid
import shutil

from ..services.cv_analyzer_workflow import CVAnalyzerWorkflowService
from ..models.schemas import AnalysisResult
from ..services.path_utils import get_script_path

# Configurar el logger
logger = logging.getLogger("cv_analyzer")

router = APIRouter()

# Crear una instancia del servicio workflow para endpoints que no utilizan microservicios
cv_analyzer_service = CVAnalyzerWorkflowService()

# Directorio para resultados de microservicios
RESULTS_DIR = os.path.join(os.getcwd(), "resultados")
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de Analizador de CV con arquitectura de nodos"}

def launch_microservice(file_path: str, job_description: str) -> str:
    """
    Lanza un microservicio para procesar un CV específico
    
    Args:
        file_path: Ruta al archivo CV
        job_description: Descripción del puesto
        
    Returns:
        process_id: ID único del proceso
    """
    # Generar ID único para este procesamiento
    process_id = str(uuid.uuid4())
    
    # Crear el directorio para los resultados de este proceso
    output_dir = os.path.join(RESULTS_DIR, process_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear un archivo temporal para almacenar la configuración
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as temp:
        # Guardar datos relevantes para el procesamiento
        config = {
            'process_id': process_id,
            'cv_file_path': file_path,
            'job_description': job_description,
            'output_dir': output_dir
        }
        json.dump(config, temp)
        config_path = temp.name
    
    logger.info(f"Lanzando microservicio con ID: {process_id} para archivo: {file_path}")
    
    # Iniciar el microservicio como un proceso independiente
    subprocess.Popen([
        'python', get_script_path('cv_microservice.py'),
        '--config', config_path
    ])
    
    return process_id

@router.post("/analyze-cv/")
async def analyze_cv(
    job_description: str = Form(...),
    cv_file: UploadFile = File(...)
):
    # Registrar inicio de la solicitud con timestamp
    start_time = datetime.now()
    logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Nueva solicitud de análisis de CV: {cv_file.filename}")
    
    # Verificar que el archivo sea un PDF
    if not cv_file.filename.endswith('.pdf'):
        logger.warning(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Archivo rechazado: {cv_file.filename} - No es un PDF")
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    
    try:
        # Guardar temporalmente el archivo
        file_location = f"temp_{cv_file.filename}"
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Guardando archivo temporal: {file_location}")
        
        with open(file_location, "wb") as file_object:
            file_content = await cv_file.read()
            file_size = len(file_content) / 1024
            file_object.write(file_content)
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Archivo guardado: {file_location} ({file_size:.2f} KB)")
        
        # Lanzar un microservicio para procesar este CV
        process_id = launch_microservice(file_location, job_description)
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Microservicio iniciado con ID: {process_id}")
        
        # Devolver una respuesta inmediata con el ID del proceso
        return {
            "message": "Análisis de CV iniciado en un microservicio independiente",
            "process_id": process_id,
            "status": "processing",
            "results_endpoint": f"/cv-results/{process_id}"
        }
    
    except Exception as e:
        # Asegurarse de eliminar el archivo temporal en caso de error
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Archivo temporal eliminado después de error: {file_location}")
        
        error_time = datetime.now()
        logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] Error al procesar el archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

@router.get("/cv-results/{process_id}")
async def get_cv_results(process_id: str):
    """
    Obtiene los resultados del análisis de un CV específico por su ID de proceso
    """
    try:
        # Buscar el archivo de resultados
        result_path = os.path.join(RESULTS_DIR, process_id, f"resultado_{process_id}.json")
        error_path = os.path.join(RESULTS_DIR, process_id, f"error_{process_id}.json")
        
        # Verificar si el proceso ha terminado
        if os.path.exists(result_path):
            # Cargar los resultados
            with open(result_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            return {
                "status": "completed",
                "process_id": process_id,
                "results": results
            }
        elif os.path.exists(error_path):
            # Cargar información de error
            with open(error_path, 'r', encoding='utf-8') as f:
                error_info = json.load(f)
            return {
                "status": "error",
                "process_id": process_id,
                "error": error_info
            }
        else:
            # El proceso sigue en ejecución
            return {
                "status": "processing",
                "process_id": process_id,
                "message": "El análisis de CV está en progreso. Por favor, intente nuevamente más tarde."
            }
    
    except Exception as e:
        logger.error(f"Error al obtener resultados para proceso {process_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow-status/")
async def get_workflow_status():
    """Endpoint para obtener el estado actual del flujo de trabajo"""
    try:
        status = cv_analyzer_service.get_workflow_status()
        return status.model_dump()
    except Exception as e:
        logger.error(f"Error al obtener el estado del flujo de trabajo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-caches/")
async def clear_caches():
    """
    Limpia las cachés del servicio
    """
    try:
        cv_analyzer_service.clear_caches()
        return {"message": "Cachés limpiadas correctamente"}
    except Exception as e:
        logger.error(f"Error al limpiar cachés: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-results/")
async def clear_results():
    """
    Limpia los resultados antiguos de análisis de CVs
    """
    try:
        # Eliminar directorios de resultados antiguos
        if os.path.exists(RESULTS_DIR):
            # Listar todos los directorios de resultados
            result_dirs = [os.path.join(RESULTS_DIR, d) for d in os.listdir(RESULTS_DIR) 
                          if os.path.isdir(os.path.join(RESULTS_DIR, d))]
            
            # Eliminar cada directorio
            for dir_path in result_dirs:
                shutil.rmtree(dir_path)
            
            logger.info(f"Se han eliminado {len(result_dirs)} directorios de resultados antiguos")
        
        return {"message": f"Se han eliminado {len(result_dirs) if 'result_dirs' in locals() else 0} directorios de resultados antiguos"}
    except Exception as e:
        logger.error(f"Error al limpiar resultados antiguos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 