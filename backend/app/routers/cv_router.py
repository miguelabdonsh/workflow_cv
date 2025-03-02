from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json

from ..services.cv_analyzer_workflow import CVAnalyzerWorkflowService
from ..models.schemas import AnalysisResult

# Configurar el logger
logger = logging.getLogger("cv_analyzer")

router = APIRouter()

# Crear una instancia del servicio workflow
cv_analyzer_service = CVAnalyzerWorkflowService()

@router.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de Analizador de CV con arquitectura de nodos"}

@router.post("/analyze-cv/")
async def analyze_cv(
    job_description: str = Form(...),
    cv_file: UploadFile = File(...)
):
    # Registrar inicio de la solicitud
    start_time = datetime.now()
    logger.info(f"Nueva solicitud de análisis de CV: {cv_file.filename}")
    
    # Verificar que el archivo sea un PDF
    if not cv_file.filename.endswith('.pdf'):
        logger.warning(f"Archivo rechazado: {cv_file.filename} - No es un PDF")
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    
    try:
        # Guardar temporalmente el archivo
        file_location = f"temp_{cv_file.filename}"
        logger.info(f"Guardando archivo temporal: {file_location}")
        
        with open(file_location, "wb") as file_object:
            file_content = await cv_file.read()
            file_object.write(file_content)
            logger.info(f"Archivo guardado: {file_location} ({len(file_content) / 1024:.2f} KB)")
        
        # Analizar el CV usando el servicio de flujo de trabajo
        logger.info("Iniciando análisis del CV con arquitectura de nodos")
        cv_analysis = await cv_analyzer_service.analyze_cv(file_location, job_description)
        
        # Eliminar el archivo temporal
        os.remove(file_location)
        logger.info(f"Archivo temporal eliminado: {file_location}")
        
        # Calcular tiempo total de procesamiento
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Análisis completado en {duration:.2f} segundos")
        
        return cv_analysis
    
    except Exception as e:
        # Asegurarse de eliminar el archivo temporal en caso de error
        if os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"Archivo temporal eliminado después de error: {file_location}")
        
        logger.error(f"Error al procesar el archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

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
    """Endpoint para limpiar las cachés de todos los nodos"""
    try:
        cv_analyzer_service.clear_caches()
        return {"message": "Todas las cachés han sido limpiadas correctamente"}
    except Exception as e:
        logger.error(f"Error al limpiar las cachés: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 