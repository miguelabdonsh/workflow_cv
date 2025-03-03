import os
import sys
import json
import logging
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cv_analyzer.microservice")

# Cargar variables de entorno
load_dotenv()

# Asegurar que podemos importar los módulos requeridos
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.services.cv_analyzer_workflow import CVAnalyzerWorkflowService
from app.models.schemas import AnalysisResult

class CVMicroservice:
    """
    Microservicio independiente para procesar un CV individual
    """
    def __init__(self, process_id, cv_file_path, job_description, output_dir):
        self.process_id = process_id
        self.cv_file_path = cv_file_path
        self.job_description = job_description
        self.output_dir = output_dir
        self.workflow_service = CVAnalyzerWorkflowService()
        logger.info(f"Microservicio {process_id} iniciado para archivo: {cv_file_path}")

    async def process(self):
        """
        Procesa el CV usando el workflow existente y guarda los resultados
        """
        try:
            logger.info(f"Iniciando análisis del CV: {self.cv_file_path}")
            start_time = datetime.now()
            
            # Ejecutar el análisis usando el servicio de workflow existente
            result = await self.workflow_service.analyze_cv(
                self.cv_file_path, 
                self.job_description
            )
            
            # Calcular tiempo de procesamiento
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Análisis completado en {duration:.2f} segundos")
            
            # Guardar resultados
            self._save_results(result)
            
            # Limpiar archivos temporales
            self._cleanup_temp_files()
            
            logger.info(f"Microservicio {self.process_id} completado exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"Error en microservicio {self.process_id}: {str(e)}")
            self._save_error(str(e))
            # Intentar limpiar archivos incluso en caso de error
            self._cleanup_temp_files()
            raise

    def _save_results(self, result: AnalysisResult):
        """
        Guarda los resultados del análisis en el directorio de salida
        """
        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Guardar resultados como JSON
        output_file = os.path.join(self.output_dir, f"resultado_{self.process_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convertir AnalysisResult a diccionario
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Resultados guardados en: {output_file}")

    def _save_error(self, error_message):
        """
        Guarda información de error en caso de fallo
        """
        os.makedirs(self.output_dir, exist_ok=True)
        error_file = os.path.join(self.output_dir, f"error_{self.process_id}.json")
        
        with open(error_file, 'w', encoding='utf-8') as f:
            error_data = {
                "process_id": self.process_id,
                "cv_file": self.cv_file_path,
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Información de error guardada en: {error_file}")
    
    def _cleanup_temp_files(self):
        """
        Limpia archivos temporales después del procesamiento
        """
        try:
            # Eliminar el archivo temporal del CV
            if os.path.exists(self.cv_file_path):
                os.remove(self.cv_file_path)
                logger.info(f"Archivo temporal eliminado: {self.cv_file_path}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar el archivo temporal {self.cv_file_path}: {str(e)}")

async def main():
    """
    Punto de entrada principal para el microservicio
    """
    parser = argparse.ArgumentParser(description='Microservicio de análisis de CV')
    parser.add_argument('--config', required=True, help='Ruta al archivo de configuración JSON')
    args = parser.parse_args()
    
    try:
        # Cargar configuración
        with open(args.config, 'r') as config_file:
            config = json.load(config_file)
        
        # Extraer parámetros
        process_id = config.get('process_id', str(datetime.now().timestamp()))
        cv_file_path = config.get('cv_file_path')
        job_description = config.get('job_description', '')
        output_dir = config.get('output_dir', os.path.join('resultados', process_id))
        
        if not cv_file_path:
            logger.error("Configuración inválida: falta cv_file_path")
            sys.exit(1)
        
        # Iniciar y ejecutar el microservicio
        microservice = CVMicroservice(process_id, cv_file_path, job_description, output_dir)
        await microservice.process()
        
        # Limpiar archivo de configuración
        try:
            os.remove(args.config)
            logger.info(f"Archivo de configuración eliminado: {args.config}")
        except:
            logger.warning(f"No se pudo eliminar el archivo de configuración: {args.config}")
        
    except Exception as e:
        logger.error(f"Error en microservicio: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 