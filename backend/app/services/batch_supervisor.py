import os
import sys
import json
import time
import logging
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import statistics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cv_analyzer.batch_supervisor")

# Asegurar que podemos importar los módulos requeridos
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.models.batch_schemas import BatchMetadata, BatchStatus, BatchResult, CVProcessInfo

class BatchSupervisor:
    """
    Microservicio supervisor para monitorear y consolidar resultados de procesamiento
    por lotes de CVs
    """
    def __init__(self, batch_id: str, metadata_path: str, results_dir: str, check_interval: int = 5):
        """
        Inicializa el supervisor de lotes
        
        Args:
            batch_id: ID único del lote
            metadata_path: Ruta al archivo de metadatos del lote
            results_dir: Directorio base donde se almacenan resultados
            check_interval: Intervalo en segundos para verificar el estado de los procesos
        """
        self.batch_id = batch_id
        self.metadata_path = metadata_path
        self.results_dir = results_dir
        self.check_interval = check_interval
        self.batch_dir = os.path.join(results_dir, f"batch_{batch_id}")
        self.consolidated_path = os.path.join(self.batch_dir, f"consolidated_{batch_id}.json")
        logger.info(f"Supervisor para lote {batch_id} inicializado")
        
    async def monitor(self) -> BatchResult:
        """
        Monitorea el progreso de un lote de CVs hasta que todos sean procesados
        """
        logger.info(f"Iniciando monitoreo del lote {self.batch_id}")
        
        # Cargar los metadatos del lote
        metadata = self._load_metadata()
        if not metadata:
            logger.error(f"No se pudieron cargar los metadatos del lote {self.batch_id}")
            return self._create_failed_result("No se pudieron cargar los metadatos del lote")
        
        # Actualizar estado a 'procesando'
        metadata.status = BatchStatus.PROCESSING
        metadata.start_processing_time = datetime.now()
        self._save_metadata(metadata)
        
        # Bucle principal de monitoreo
        try:
            while not metadata.is_complete:
                logger.info(f"Verificando estado del lote {self.batch_id}: "
                           f"{metadata.processed_cvs}/{metadata.total_cvs} completados")
                
                updated = await self._check_processes_status(metadata)
                if updated:
                    self._save_metadata(metadata)
                
                if metadata.is_complete:
                    break
                    
                # Esperar antes de la siguiente verificación
                await asyncio.sleep(self.check_interval)
                
                # Recargar metadatos (por si otro proceso los modificó)
                metadata = self._load_metadata()
            
            # Finalizar el procesamiento
            logger.info(f"Lote {self.batch_id} completado. Generando resultados consolidados")
            return await self._consolidate_results(metadata)
            
        except Exception as e:
            logger.error(f"Error monitoreando el lote {self.batch_id}: {str(e)}")
            metadata.status = BatchStatus.FAILED
            self._save_metadata(metadata)
            return self._create_failed_result(str(e))
    
    async def _check_processes_status(self, metadata: BatchMetadata) -> bool:
        """
        Verifica el estado de cada proceso en el lote
        
        Returns:
            bool: True si algún estado fue actualizado, False en caso contrario
        """
        updated = False
        
        for process_id, process_info in metadata.processes.items():
            # Saltar procesos ya completados o fallidos
            if process_info.status in ["completed", "failed"]:
                continue
                
            # Verificar archivo de resultados
            result_path = os.path.join(self.results_dir, process_id, f"resultado_{process_id}.json")
            error_path = os.path.join(self.results_dir, process_id, f"error_{process_id}.json")
            
            if os.path.exists(result_path):
                # Proceso completado exitosamente
                try:
                    with open(result_path, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        match_score = result_data.get("match_score", 0.0)
                    
                    process_info.status = "completed"
                    process_info.end_time = datetime.now()
                    process_info.match_score = match_score
                    
                    if process_info.start_time:
                        process_info.duration_seconds = (
                            process_info.end_time - process_info.start_time
                        ).total_seconds()
                    
                    metadata.processed_cvs += 1
                    metadata.successful_cvs += 1
                    updated = True
                    logger.info(f"Proceso {process_id} completado con éxito")
                    
                except Exception as e:
                    logger.error(f"Error al leer resultados de {process_id}: {str(e)}")
                    process_info.status = "failed"
                    process_info.error = f"Error al leer resultados: {str(e)}"
                    metadata.processed_cvs += 1
                    metadata.failed_cvs += 1
                    updated = True
            
            elif os.path.exists(error_path):
                # Proceso falló
                try:
                    with open(error_path, 'r', encoding='utf-8') as f:
                        error_data = json.load(f)
                        error_message = error_data.get("error", "Error desconocido")
                    
                    process_info.status = "failed"
                    process_info.end_time = datetime.now()
                    process_info.error = error_message
                    
                    if process_info.start_time:
                        process_info.duration_seconds = (
                            process_info.end_time - process_info.start_time
                        ).total_seconds()
                    
                    metadata.processed_cvs += 1
                    metadata.failed_cvs += 1
                    updated = True
                    logger.info(f"Proceso {process_id} falló: {error_message}")
                    
                except Exception as e:
                    logger.error(f"Error al leer error de {process_id}: {str(e)}")
                    process_info.status = "failed"
                    process_info.error = f"Error al leer datos de error: {str(e)}"
                    metadata.processed_cvs += 1
                    metadata.failed_cvs += 1
                    updated = True
        
        # Actualizar estado general del lote
        if metadata.is_complete:
            metadata.status = BatchStatus.COMPLETED
            metadata.completion_time = datetime.now()
            updated = True
        
        return updated
            
    async def _consolidate_results(self, metadata: BatchMetadata) -> BatchResult:
        """
        Consolida los resultados de todos los procesos en un único resultado
        """
        logger.info(f"Consolidando resultados para el lote {self.batch_id}")
        
        # Recopilar resultados y organizarlos
        cv_results = []
        match_scores = []
        
        for process_id, process_info in metadata.processes.items():
            if process_info.status == "completed":
                result_path = os.path.join(self.results_dir, process_id, f"resultado_{process_id}.json")
                
                try:
                    with open(result_path, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    
                    # Añadir metadata del proceso
                    result_data["process_metadata"] = {
                        "process_id": process_id,
                        "filename": process_info.filename,
                        "duration_seconds": process_info.duration_seconds,
                        "start_time": process_info.start_time.isoformat() if process_info.start_time else None,
                        "end_time": process_info.end_time.isoformat() if process_info.end_time else None
                    }
                    
                    cv_results.append(result_data)
                    
                    if "match_score" in result_data:
                        match_scores.append(result_data["match_score"])
                        
                except Exception as e:
                    logger.error(f"Error al consolidar resultados de {process_id}: {str(e)}")
        
        # Ordenar por puntuación de compatibilidad (descendente)
        cv_results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Seleccionar los mejores candidatos (top 5 o todos si hay menos)
        top_candidates = cv_results[:min(5, len(cv_results))]
        
        # Calcular estadísticas
        avg_score = statistics.mean(match_scores) if match_scores else None
        
        # Generar informe comparativo
        comparison_summary = self._generate_comparison_summary(cv_results)
        
        # Crear resultado consolidado
        result = BatchResult(
            batch_id=self.batch_id,
            job_description=metadata.job_description,
            status=metadata.status,
            total_cvs=metadata.total_cvs,
            processed_cvs=metadata.processed_cvs,
            successful_cvs=metadata.successful_cvs,
            failed_cvs=metadata.failed_cvs,
            creation_time=metadata.creation_time,
            start_processing_time=metadata.start_processing_time,
            completion_time=metadata.completion_time,
            total_duration_seconds=(
                (metadata.completion_time - metadata.start_processing_time).total_seconds()
                if metadata.completion_time and metadata.start_processing_time
                else None
            ),
            cv_results=cv_results,
            top_candidates=top_candidates,
            average_match_score=avg_score,
            comparison_summary=comparison_summary
        )
        
        # Guardar resultados consolidados
        self._save_consolidated_results(result)
        logger.info(f"Resultados consolidados para el lote {self.batch_id} guardados exitosamente")
        
        return result
    
    def _generate_comparison_summary(self, cv_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un resumen comparativo de los resultados
        """
        if not cv_results:
            return {"message": "No hay resultados para comparar"}
        
        # Extraer información relevante para la comparación
        candidates_info = []
        skills_frequency = {}
        
        for result in cv_results:
            cv_data = result.get("cv_data", {})
            match_score = result.get("match_score", 0)
            
            # Información básica del candidato
            candidate = {
                "nombre": cv_data.get("nombre", "Desconocido"),
                "match_score": match_score,
                "fortalezas": result.get("fortalezas", [])[:3],  # Top 3 fortalezas
                "habilidades_tecnicas": cv_data.get("habilidades_tecnicas", [])
            }
            candidates_info.append(candidate)
            
            # Contar frecuencia de habilidades
            for skill in cv_data.get("habilidades_tecnicas", []):
                if skill in skills_frequency:
                    skills_frequency[skill] += 1
                else:
                    skills_frequency[skill] = 1
        
        # Ordenar habilidades por frecuencia
        common_skills = sorted(
            skills_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 habilidades comunes
        
        # Crear resumen comparativo
        summary = {
            "total_candidates": len(cv_results),
            "candidates_brief": candidates_info,
            "common_skills": [{"skill": skill, "frequency": freq} for skill, freq in common_skills],
            "score_distribution": self._calculate_score_distribution([r.get("match_score", 0) for r in cv_results])
        }
        
        return summary
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """
        Calcula la distribución de puntuaciones en rangos
        """
        ranges = {
            "0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        for score in scores:
            if score < 0.2:
                ranges["0-0.2"] += 1
            elif score < 0.4:
                ranges["0.2-0.4"] += 1
            elif score < 0.6:
                ranges["0.4-0.6"] += 1
            elif score < 0.8:
                ranges["0.6-0.8"] += 1
            else:
                ranges["0.8-1.0"] += 1
                
        return ranges
    
    def _load_metadata(self) -> Optional[BatchMetadata]:
        """
        Carga los metadatos del lote desde el archivo
        """
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return BatchMetadata.model_validate(data)
        except Exception as e:
            logger.error(f"Error al cargar metadatos del lote {self.batch_id}: {str(e)}")
            return None
    
    def _save_metadata(self, metadata: BatchMetadata) -> None:
        """
        Guarda los metadatos del lote en el archivo
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
            
            # Convertir a diccionario y guardar
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.model_dump(), f, default=str, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error al guardar metadatos del lote {self.batch_id}: {str(e)}")
    
    def _save_consolidated_results(self, result: BatchResult) -> None:
        """
        Guarda los resultados consolidados en un archivo
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.consolidated_path), exist_ok=True)
            
            # Convertir a diccionario y guardar
            with open(self.consolidated_path, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, default=str, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error al guardar resultados consolidados del lote {self.batch_id}: {str(e)}")
    
    def _create_failed_result(self, error_message: str) -> BatchResult:
        """
        Crea un resultado para un lote fallido
        """
        metadata = self._load_metadata()
        if not metadata:
            # Crear metadatos básicos si no se pudieron cargar
            metadata = BatchMetadata(
                batch_id=self.batch_id,
                job_description="",
                total_cvs=0,
                status=BatchStatus.FAILED
            )
        else:
            metadata.status = BatchStatus.FAILED
            
        return BatchResult(
            batch_id=self.batch_id,
            job_description=metadata.job_description,
            status=BatchStatus.FAILED,
            total_cvs=metadata.total_cvs,
            processed_cvs=metadata.processed_cvs,
            successful_cvs=metadata.successful_cvs,
            failed_cvs=metadata.failed_cvs,
            creation_time=metadata.creation_time,
            start_processing_time=metadata.start_processing_time,
            completion_time=datetime.now(),
            comparison_summary={"error": error_message}
        )


async def main():
    """
    Punto de entrada principal para el microservicio supervisor
    """
    parser = argparse.ArgumentParser(description='Supervisor de procesamiento por lotes de CVs')
    parser.add_argument('--batch-id', required=True, help='ID del lote a supervisar')
    parser.add_argument('--metadata-path', required=True, help='Ruta al archivo de metadatos del lote')
    parser.add_argument('--results-dir', required=True, help='Directorio base de resultados')
    parser.add_argument('--check-interval', type=int, default=5, help='Intervalo de verificación en segundos')
    
    args = parser.parse_args()
    
    try:
        # Iniciar el supervisor
        supervisor = BatchSupervisor(
            batch_id=args.batch_id,
            metadata_path=args.metadata_path,
            results_dir=args.results_dir,
            check_interval=args.check_interval
        )
        
        # Monitorear hasta que todos los procesos terminen
        result = await supervisor.monitor()
        logger.info(f"Supervisión del lote {args.batch_id} completada")
        
    except Exception as e:
        logger.error(f"Error en el supervisor de lotes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 