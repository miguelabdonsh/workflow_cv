from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from ..services.batch_processor import BatchProcessor
from ..models.batch_schemas import BatchSubmission, BatchProgressResponse, BatchStatus

# Configurar el logger
logger = logging.getLogger("cv_analyzer.batch_router")

router = APIRouter()

# Crear una instancia del procesador de lotes
batch_processor = BatchProcessor()

@router.post("/batch-cv/")
async def process_cv_batch(
    job_description: str = Form(...),
    cv_files: List[UploadFile] = File(...)
):
    """
    Inicia el procesamiento de un lote de CVs 
    
    Cada CV se procesará en un microservicio independiente y
    un supervisor coordinará y consolidará los resultados.
    """
    # Validar que se hayan enviado CVs
    if not cv_files:
        raise HTTPException(status_code=400, detail="No se han enviado archivos CV")
        
    # Registrar inicio de la solicitud
    start_time = datetime.now()
    logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] "
               f"Nueva solicitud de procesamiento por lotes: {len(cv_files)} CVs")
    
    try:
        # Guardar temporalmente los archivos
        temp_files = []
        for cv_file in cv_files:
            # Verificar que el archivo sea un PDF
            if not cv_file.filename.endswith('.pdf'):
                logger.warning(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"Archivo rechazado: {cv_file.filename} - No es un PDF")
                continue
                
            # Guardar el archivo temporalmente
            file_location = f"temp_batch_{start_time.strftime('%Y%m%d%H%M%S')}_{cv_file.filename}"
            with open(file_location, "wb") as file_object:
                file_content = await cv_file.read()
                file_size = len(file_content) / 1024
                file_object.write(file_content)
                logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                           f"Archivo guardado: {file_location} ({file_size:.2f} KB)")
            
            # Registrar información del archivo
            temp_files.append({
                "file_path": file_location,
                "filename": cv_file.filename,
                "file_size": file_size
            })
        
        # Verificar que haya archivos válidos
        if not temp_files:
            raise HTTPException(status_code=400, detail="No se han enviado archivos PDF válidos")
        
        # Iniciar procesamiento por lotes
        batch_id = await batch_processor.process_batch(temp_files, job_description)
        
        # Registrar información
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                   f"Lote iniciado con ID: {batch_id}, {len(temp_files)} CVs")
        
        # Responder con ID del lote y endpoint para consultar resultados
        return {
            "message": f"Procesamiento por lotes iniciado con {len(temp_files)} CVs",
            "batch_id": batch_id,
            "status": "processing",
            "total_cvs": len(temp_files),
            "results_endpoint": f"/batch-results/{batch_id}"
        }
    
    except Exception as e:
        # Limpiar archivos temporales en caso de error
        for file_info in temp_files:
            file_path = file_info.get("file_path")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                           f"Archivo temporal eliminado después de error: {file_path}")
        
        error_time = datetime.now()
        logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Error al procesar lote de CVs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar lote de CVs: {str(e)}")

@router.get("/batch-results/{batch_id}")
async def get_batch_results(batch_id: str):
    """
    Obtiene los resultados de un procesamiento por lotes
    
    Si el procesamiento aún no ha terminado, devuelve información
    sobre el progreso actual.
    """
    try:
        # Obtener información del lote
        batch_data = batch_processor.get_batch_results(batch_id)
        
        if not batch_data:
            raise HTTPException(status_code=404, detail=f"No se encontró el lote con ID {batch_id}")
        
        # Verificar si ya hay resultados consolidados
        if "cv_results" in batch_data:
            # El procesamiento ha terminado, devolver resultados completos
            return {
                "status": "completed",
                "batch_id": batch_id,
                "results": batch_data
            }
        
        # El procesamiento sigue en curso, calcular progreso
        status = batch_data.get("status", "pending")
        total_cvs = batch_data.get("total_cvs", 0)
        processed_cvs = batch_data.get("processed_cvs", 0)
        
        progress_percentage = 0
        if total_cvs > 0:
            progress_percentage = int((processed_cvs / total_cvs) * 100)
            
        return {
            "status": status,
            "batch_id": batch_id,
            "progress": {
                "processed_cvs": processed_cvs,
                "total_cvs": total_cvs,
                "percentage": progress_percentage
            },
            "message": f"El procesamiento del lote está en progreso ({progress_percentage}% completado)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener resultados del lote {batch_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-status/{batch_id}")
async def get_batch_status(batch_id: str):
    """
    Obtiene información sobre el estado actual de un lote
    """
    try:
        # Obtener información del lote
        batch_data = batch_processor.get_batch_status(batch_id)
        
        if not batch_data:
            raise HTTPException(status_code=404, detail=f"No se encontró el lote con ID {batch_id}")
            
        # Devolver información de estado
        return {
            "batch_id": batch_id,
            "status": batch_data.get("status", "unknown"),
            "total_cvs": batch_data.get("total_cvs", 0),
            "processed_cvs": batch_data.get("processed_cvs", 0),
            "successful_cvs": batch_data.get("successful_cvs", 0),
            "failed_cvs": batch_data.get("failed_cvs", 0),
            "creation_time": batch_data.get("creation_time"),
            "start_processing_time": batch_data.get("start_processing_time"),
            "completion_time": batch_data.get("completion_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener estado del lote {batch_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 