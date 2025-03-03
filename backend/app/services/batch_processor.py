import os
import json
import uuid
import logging
import tempfile
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models.batch_schemas import BatchMetadata, BatchStatus, CVProcessInfo
from ..services.path_utils import get_script_path

# Configurar el logger
logger = logging.getLogger("cv_analyzer.batch_processor")

class BatchProcessor:
    """
    Servicio para gestionar el procesamiento de múltiples CVs por lotes
    """
    def __init__(self, results_dir: str = None):
        """
        Inicializa el procesador de lotes
        
        Args:
            results_dir: Directorio base para almacenar resultados
        """
        self.results_dir = results_dir or os.path.join(os.getcwd(), "resultados")
        os.makedirs(self.results_dir, exist_ok=True)
        
    async def process_batch(self, cv_files: List[Dict[str, Any]], job_description: str) -> str:
        """
        Inicia el procesamiento de un lote de CVs
        
        Args:
            cv_files: Lista de diccionarios con información de archivos CV
                      [{"file_path": str, "filename": str}, ...]
            job_description: Descripción del puesto
            
        Returns:
            batch_id: ID único del lote
        """
        # Generar ID único para el lote
        batch_id = str(uuid.uuid4())
        logger.info(f"Iniciando procesamiento de lote {batch_id} con {len(cv_files)} CVs")
        
        # Crear directorio para este lote
        batch_dir = os.path.join(self.results_dir, f"batch_{batch_id}")
        os.makedirs(batch_dir, exist_ok=True)
        
        # Preparar metadatos del lote
        metadata = BatchMetadata(
            batch_id=batch_id,
            job_description=job_description,
            status=BatchStatus.PENDING,
            total_cvs=len(cv_files),
            creation_time=datetime.now()
        )
        
        # Iniciar microservicios para cada CV
        processes = {}
        for cv_info in cv_files:
            try:
                # Extraer información del CV
                file_path = cv_info["file_path"]
                filename = cv_info["filename"]
                
                # Iniciar procesamiento individual
                process_id = self._launch_cv_microservice(file_path, job_description)
                
                # Registrar información del proceso
                processes[process_id] = CVProcessInfo(
                    process_id=process_id,
                    filename=filename,
                    file_path=file_path,
                    status="pending",
                    start_time=datetime.now()
                )
                
                logger.info(f"Microservicio iniciado para CV {filename} con ID: {process_id}")
                
            except Exception as e:
                logger.error(f"Error al iniciar microservicio para {cv_info.get('filename', 'desconocido')}: {str(e)}")
        
        # Actualizar metadatos con la información de procesos
        metadata.processes = processes
        
        # Guardar metadatos del lote
        metadata_path = os.path.join(batch_dir, f"metadata_{batch_id}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.model_dump(), f, default=str, ensure_ascii=False, indent=2)
        
        # Iniciar el supervisor
        self._launch_supervisor(batch_id, metadata_path)
        
        return batch_id
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado actual de un lote
        
        Args:
            batch_id: ID del lote
            
        Returns:
            Diccionario con información del estado o None si no se encuentra
        """
        try:
            # Verificar metadatos del lote
            batch_dir = os.path.join(self.results_dir, f"batch_{batch_id}")
            metadata_path = os.path.join(batch_dir, f"metadata_{batch_id}.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata
            
            # Verificar si hay resultados consolidados
            consolidated_path = os.path.join(batch_dir, f"consolidated_{batch_id}.json")
            if os.path.exists(consolidated_path):
                with open(consolidated_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                return results
                
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener estado del lote {batch_id}: {str(e)}")
            return None
    
    def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los resultados consolidados de un lote
        
        Args:
            batch_id: ID del lote
            
        Returns:
            Diccionario con resultados consolidados o None si no están disponibles
        """
        try:
            # Verificar si hay resultados consolidados
            batch_dir = os.path.join(self.results_dir, f"batch_{batch_id}")
            consolidated_path = os.path.join(batch_dir, f"consolidated_{batch_id}.json")
            
            if os.path.exists(consolidated_path):
                with open(consolidated_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                return results
            
            # Si no hay resultados consolidados, devolver estado actual
            return self.get_batch_status(batch_id)
            
        except Exception as e:
            logger.error(f"Error al obtener resultados del lote {batch_id}: {str(e)}")
            return None
    
    def _launch_cv_microservice(self, file_path: str, job_description: str) -> str:
        """
        Lanza un microservicio para procesar un CV individual
        
        Args:
            file_path: Ruta al archivo CV
            job_description: Descripción del puesto
            
        Returns:
            process_id: ID único del proceso
        """
        # Generar ID único para el proceso
        process_id = str(uuid.uuid4())
        
        # Crear directorio para los resultados de este proceso
        output_dir = os.path.join(self.results_dir, process_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear archivo de configuración
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as temp:
            config = {
                'process_id': process_id,
                'cv_file_path': file_path,
                'job_description': job_description,
                'output_dir': output_dir
            }
            json.dump(config, temp)
            config_path = temp.name
        
        # Iniciar el microservicio como proceso independiente
        subprocess.Popen([
            'python', get_script_path('cv_microservice.py'),
            '--config', config_path
        ])
        
        return process_id
    
    def _launch_supervisor(self, batch_id: str, metadata_path: str) -> None:
        """
        Lanza el supervisor para monitorear un lote de procesamiento
        
        Args:
            batch_id: ID del lote
            metadata_path: Ruta al archivo de metadatos
        """
        try:
            # Iniciar supervisor como proceso independiente
            subprocess.Popen([
                'python', get_script_path('batch_supervisor.py'),
                '--batch-id', batch_id,
                '--metadata-path', metadata_path,
                '--results-dir', self.results_dir,
                '--check-interval', '5'
            ])
            
            logger.info(f"Supervisor iniciado para lote {batch_id}")
            
        except Exception as e:
            logger.error(f"Error al iniciar supervisor para lote {batch_id}: {str(e)}") 