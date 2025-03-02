from typing import Dict, List, Any, Optional, Callable, TypeVar, Type, Union, Awaitable
import asyncio
import logging
from pydantic import BaseModel
from datetime import datetime

from .base_node import BaseNode, NodeMetadata

# Configurar el logger
logger = logging.getLogger("cv_analyzer.workflow")

T = TypeVar('T', bound=BaseModel)

class WorkflowMetadata(BaseModel):
    """Metadatos sobre la ejecución del flujo de trabajo"""
    workflow_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    node_metadata: Dict[str, NodeMetadata] = {}

class WorkflowStatus(BaseModel):
    """Estado actual del flujo de trabajo"""
    is_running: bool = False
    current_node: Optional[str] = None
    completed_nodes: List[str] = []
    pending_nodes: List[str] = []
    failed_nodes: List[str] = []
    start_time: Optional[datetime] = None
    progress_percentage: float = 0.0

class NodeConnection(BaseModel):
    """Representa una conexión entre nodos en el flujo de trabajo"""
    from_node: str
    to_node: str
    condition: Optional[Callable] = None

class WorkflowManager:
    """Gestor del flujo de trabajo entre nodos"""
    
    def __init__(self, name: str = "CVAnalysisWorkflow"):
        self.name = name
        self.nodes: Dict[str, BaseNode] = {}
        self.connections: List[NodeConnection] = []
        self.status = WorkflowStatus()
        self.metadata_history: List[WorkflowMetadata] = []
    
    def add_node(self, node: BaseNode) -> None:
        """Añade un nodo al flujo de trabajo"""
        self.nodes[node.name] = node
        self.status.pending_nodes.append(node.name)
        logger.info(f"Node {node.name} added to workflow {self.name}")
    
    def connect(self, from_node: Union[str, BaseNode], to_node: Union[str, BaseNode], 
                condition: Optional[Callable] = None) -> None:
        """Conecta dos nodos en el flujo de trabajo"""
        from_name = from_node if isinstance(from_node, str) else from_node.name
        to_name = to_node if isinstance(to_node, str) else to_node.name
        
        if from_name not in self.nodes:
            raise ValueError(f"Node {from_name} not found in workflow")
        if to_name not in self.nodes:
            raise ValueError(f"Node {to_name} not found in workflow")
        
        connection = NodeConnection(from_node=from_name, to_node=to_name, condition=condition)
        self.connections.append(connection)
        logger.info(f"Connected {from_name} to {to_name} in workflow {self.name}")
    
    def _get_next_nodes(self, current_node: str, context: Dict[str, Any]) -> List[str]:
        """Determina los siguientes nodos a ejecutar basándose en las conexiones"""
        next_nodes = []
        
        for conn in self.connections:
            if conn.from_node == current_node:
                # Si hay una condición, evaluarla
                if conn.condition is None or conn.condition(context):
                    next_nodes.append(conn.to_node)
        
        return next_nodes
    
    async def execute(self, start_node: str, initial_input: BaseModel, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ejecuta el flujo de trabajo comenzando desde un nodo específico"""
        if start_node not in self.nodes:
            raise ValueError(f"Start node {start_node} not found in workflow")
        
        # Inicializar estado y metadatos
        self.status = WorkflowStatus(
            is_running=True,
            current_node=start_node,
            pending_nodes=[n for n in self.nodes.keys()],
            completed_nodes=[],
            failed_nodes=[],
            start_time=datetime.now()
        )
        
        metadata = WorkflowMetadata(
            workflow_name=self.name,
            start_time=datetime.now()
        )
        
        start_time_ms = datetime.now().timestamp() * 1000
        workflow_context = context or {}
        node_outputs = {}
        current_input = initial_input
        
        try:
            # Iniciar desde el nodo de inicio
            queue = [(start_node, current_input)]
            processed_nodes = set()
            
            while queue:
                current_node_name, node_input = queue.pop(0)
                
                # Actualizar estado
                self.status.current_node = current_node_name
                self.status.pending_nodes.remove(current_node_name)
                
                # Obtener nodo actual
                current_node = self.nodes[current_node_name]
                
                try:
                    # Ejecutar nodo actual
                    logger.info(f"Executing node {current_node_name} in workflow {self.name}")
                    output, node_metadata = await current_node.execute(node_input, workflow_context)
                    
                    # Guardar salida y metadatos
                    node_outputs[current_node_name] = output
                    metadata.node_metadata[current_node_name] = node_metadata
                    
                    # Marcar como completado
                    self.status.completed_nodes.append(current_node_name)
                    processed_nodes.add(current_node_name)
                    
                    # Encontrar nodos siguientes
                    next_nodes = self._get_next_nodes(current_node_name, workflow_context)
                    
                    # Encolar nodos siguientes
                    for next_node in next_nodes:
                        if next_node not in processed_nodes:
                            queue.append((next_node, output))
                
                except Exception as e:
                    logger.error(f"Error executing node {current_node_name}: {str(e)}")
                    self.status.failed_nodes.append(current_node_name)
                    metadata.error_message = f"Error in node {current_node_name}: {str(e)}"
                    raise
                
                # Actualizar progreso
                total_nodes = len(self.nodes)
                completed_nodes = len(self.status.completed_nodes)
                self.status.progress_percentage = (completed_nodes / total_nodes) * 100
            
            # Finalizar correctamente
            end_time_ms = datetime.now().timestamp() * 1000
            metadata.end_time = datetime.now()
            metadata.execution_time_ms = end_time_ms - start_time_ms
            metadata.success = True
            
            self.status.is_running = False
            self.metadata_history.append(metadata)
            
            return node_outputs
        
        except Exception as e:
            # Finalizar con error
            end_time_ms = datetime.now().timestamp() * 1000
            metadata.end_time = datetime.now()
            metadata.execution_time_ms = end_time_ms - start_time_ms
            metadata.success = False
            if not metadata.error_message:
                metadata.error_message = str(e)
            
            self.status.is_running = False
            self.metadata_history.append(metadata)
            
            raise
    
    async def execute_parallel(self, node_names: List[str], inputs: Dict[str, BaseModel], 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ejecuta varios nodos en paralelo"""
        tasks = []
        workflow_context = context or {}
        
        for node_name in node_names:
            if node_name not in self.nodes:
                raise ValueError(f"Node {node_name} not found in workflow")
            
            node = self.nodes[node_name]
            node_input = inputs.get(node_name)
            
            if node_input is None:
                raise ValueError(f"No input provided for node {node_name}")
            
            task = asyncio.create_task(node.execute(node_input, workflow_context))
            tasks.append((node_name, task))
        
        results = {}
        for node_name, task in tasks:
            try:
                output, metadata = await task
                results[node_name] = output
            except Exception as e:
                logger.error(f"Error executing node {node_name} in parallel: {str(e)}")
                raise
        
        return results
    
    def get_last_metadata(self) -> Optional[WorkflowMetadata]:
        """Obtiene los metadatos de la última ejecución del flujo de trabajo"""
        if not self.metadata_history:
            return None
        return self.metadata_history[-1]
    
    def clear_all_caches(self) -> None:
        """Limpia todas las cachés de todos los nodos"""
        for node in self.nodes.values():
            node.clear_cache()
        logger.info(f"All caches cleared for workflow {self.name}")
    
    def get_status(self) -> WorkflowStatus:
        """Obtiene el estado actual del flujo de trabajo"""
        return self.status 