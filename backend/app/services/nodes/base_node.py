from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Optional, Type
import logging
import time
from datetime import datetime
from pydantic import BaseModel, create_model

# Configurar el logger
logger = logging.getLogger("cv_analyzer.nodes")

# Tipo genérico para la entrada y salida de los nodos
InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)
ContextT = TypeVar('ContextT', dict, Any)

class NodeMetadata(BaseModel):
    """Metadatos sobre la ejecución del nodo"""
    node_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    cache_hit: bool = False
    input_summary: Dict[str, Any] = {}
    output_summary: Dict[str, Any] = {}

class BaseNode(Generic[InputT, OutputT, ContextT], ABC):
    """Clase base para todos los nodos del sistema de análisis de CV"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.cache = {}  # Cache simple en memoria para resultados
        self.metadata = {}  # Historial de ejecuciones
    
    @abstractmethod
    async def process(self, input_data: InputT, context: ContextT) -> OutputT:
        """Método principal para procesar los datos de entrada y generar la salida"""
        pass
    
    async def execute(self, input_data: InputT, context: ContextT = None) -> tuple[OutputT, NodeMetadata]:
        """Ejecuta el nodo, gestionando errores, caché y registro"""
        # Inicializar los metadatos
        metadata = NodeMetadata(
            node_name=self.name,
            start_time=datetime.now(),
        )
        
        # Preparar un resumen de la entrada para los metadatos
        if isinstance(input_data, BaseModel):
            metadata.input_summary = {
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                for k, v in input_data.model_dump().items()
            }
        
        # Verificar si el resultado está en caché
        cache_key = self._get_cache_key(input_data)
        if cache_key in self.cache:
            logger.info(f"Cache hit for node {self.name}")
            metadata.cache_hit = True
            metadata.end_time = datetime.now()
            metadata.success = True
            metadata.execution_time_ms = 0
            return self.cache[cache_key], metadata
        
        try:
            # Iniciar el temporizador
            start_time = time.time()
            
            # Procesar los datos
            logger.info(f"Executing node {self.name}")
            result = await self.process(input_data, context or {})
            
            # Calcular el tiempo de ejecución
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            # Actualizar metadatos
            metadata.end_time = datetime.now()
            metadata.execution_time_ms = execution_time_ms
            metadata.success = True
            
            # Preparar un resumen de la salida para los metadatos
            if isinstance(result, BaseModel):
                metadata.output_summary = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                    for k, v in result.model_dump().items()
                }
            
            # Guardar en caché
            self.cache[cache_key] = result
            
            # Registrar metadatos históricos
            self.metadata[metadata.start_time.isoformat()] = metadata
            
            return result, metadata
            
        except Exception as e:
            # Manejar errores
            logger.error(f"Error in node {self.name}: {str(e)}")
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            # Actualizar metadatos con información del error
            metadata.end_time = datetime.now()
            metadata.execution_time_ms = execution_time_ms
            metadata.success = False
            metadata.error_message = str(e)
            
            # Registrar metadatos históricos
            self.metadata[metadata.start_time.isoformat()] = metadata
            
            # Re-lanzar la excepción
            raise
    
    def _get_cache_key(self, input_data: InputT) -> str:
        """Genera una clave única para el caché basada en los datos de entrada"""
        if isinstance(input_data, BaseModel):
            # Usar los valores del modelo como clave de caché
            data_dict = input_data.model_dump_json()
            return f"{self.name}:{hash(data_dict)}"
        else:
            # Fallback para otros tipos de datos
            return f"{self.name}:{hash(str(input_data))}"
    
    def clear_cache(self):
        """Limpia el caché del nodo"""
        self.cache = {}
        logger.info(f"Cache cleared for node {self.name}")
    
    def get_metadata_history(self) -> Dict[str, NodeMetadata]:
        """Devuelve el historial de metadatos de ejecución"""
        return self.metadata
    
    def get_input_type(self) -> Type[InputT]:
        """Devuelve el tipo de entrada esperado por el nodo"""
        return self.__orig_bases__[0].__args__[0]  # type: ignore
    
    def get_output_type(self) -> Type[OutputT]:
        """Devuelve el tipo de salida producido por el nodo"""
        return self.__orig_bases__[0].__args__[1]  # type: ignore 