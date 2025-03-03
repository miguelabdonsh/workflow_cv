from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BatchStatus(str, Enum):
    """Estados posibles para un lote de procesamiento de CVs"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CVProcessInfo(BaseModel):
    """Información sobre un proceso individual de análisis de CV"""
    process_id: str
    filename: str
    file_path: str
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    match_score: Optional[float] = None
    error: Optional[str] = None


class BatchMetadata(BaseModel):
    """Metadatos de un lote de procesamiento de CVs"""
    batch_id: str
    job_description: str
    status: BatchStatus = BatchStatus.PENDING
    total_cvs: int
    processed_cvs: int = 0
    successful_cvs: int = 0
    failed_cvs: int = 0
    creation_time: datetime = Field(default_factory=datetime.now)
    start_processing_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    processes: Dict[str, CVProcessInfo] = {}
    
    @property
    def is_complete(self) -> bool:
        """Verifica si el procesamiento del lote ha terminado"""
        return self.processed_cvs >= self.total_cvs
    
    @property
    def progress_percentage(self) -> int:
        """Calcula el porcentaje de progreso"""
        if self.total_cvs == 0:
            return 0
        return int((self.processed_cvs / self.total_cvs) * 100)


class BatchResult(BaseModel):
    """Resultado consolidado del procesamiento de un lote de CVs"""
    batch_id: str
    job_description: str
    status: BatchStatus
    total_cvs: int
    processed_cvs: int
    successful_cvs: int
    failed_cvs: int
    creation_time: datetime
    start_processing_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None
    cv_results: List[Dict[str, Any]] = []
    top_candidates: List[Dict[str, Any]] = []
    average_match_score: Optional[float] = None
    comparison_summary: Optional[Dict[str, Any]] = None


class BatchSubmission(BaseModel):
    """Modelo para la creación de un nuevo lote de procesamiento"""
    job_description: str
    notify_on_completion: bool = False
    notification_email: Optional[str] = None


class BatchProgressResponse(BaseModel):
    """Respuesta con información de progreso de un lote"""
    batch_id: str
    status: BatchStatus
    progress_percentage: int
    processed_cvs: int
    total_cvs: int
    start_time: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    time_elapsed_seconds: Optional[float] = None
    time_remaining_seconds: Optional[float] = None 