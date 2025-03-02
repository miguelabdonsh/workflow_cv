from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union, Literal
from enum import Enum
from datetime import datetime

# Modelo para el documento de CV extraído
class CVDocument(BaseModel):
    """Modelo base con el texto extraído y metadatos del CV"""
    text: str
    filename: str
    file_size: int
    extraction_date: datetime = Field(default_factory=datetime.now)
    mime_type: str = "application/pdf"
    
# Modelo para la información clasificada por secciones
class ClassifiedCV(BaseModel):
    """Información del CV categorizada por secciones"""
    nombre: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    ubicacion: Optional[str] = None
    linkedin: Optional[str] = None
    resumen: Optional[str] = None
    educacion_texto: Optional[str] = None
    experiencia_texto: Optional[str] = None
    habilidades_texto: Optional[str] = None
    idiomas_texto: Optional[str] = None
    certificaciones_texto: Optional[str] = None
    proyectos_texto: Optional[str] = None
    logros_texto: Optional[str] = None
    intereses_texto: Optional[str] = None
    referencias_texto: Optional[str] = None
    secciones_adicionales: Dict[str, str] = {}
    
# Enumerados para niveles de habilidad y relevancia
class NivelHabilidad(str, Enum):
    BASICO = "Básico"
    INTERMEDIO = "Intermedio"
    AVANZADO = "Avanzado"
    EXPERTO = "Experto"

class NivelRelevancia(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    
# Modelos para la evaluación de habilidades
class HabilidadEvaluada(BaseModel):
    nombre: str
    nivel: NivelHabilidad
    relevancia: NivelRelevancia
    descripcion: Optional[str] = None
    años_experiencia: Optional[float] = None
    
class SkillsEvaluation(BaseModel):
    """Evaluación detallada de habilidades técnicas y blandas"""
    habilidades_tecnicas: List[HabilidadEvaluada] = []
    habilidades_blandas: List[HabilidadEvaluada] = []
    idiomas: List[Dict[str, str]] = []
    puntuacion_general: float = Field(ge=0.0, le=1.0)
    justificacion_puntuacion: Optional[str] = None
    campo_principal_candidato: Optional[str] = None
    campo_solicitado: Optional[str] = None
    match_campo: bool = False
    fortalezas: List[str] = []
    debilidades: List[str] = []

# Modelos para la evaluación de experiencia
class ExperienciaDetallada(BaseModel):
    empresa: str
    puesto: str
    fecha_inicio: str
    fecha_fin: str
    duracion_meses: int
    ubicacion: Optional[str] = None
    descripcion: str
    tecnologias: List[str] = []
    relevancia: NivelRelevancia
    logros_clave: List[str] = []

class ExperienceEvaluation(BaseModel):
    """Análisis detallado de la experiencia laboral"""
    experiencias: List[ExperienciaDetallada] = []
    años_experiencia_total: float
    años_experiencia_relevante: float
    puntuacion_experiencia: float = Field(ge=0.0, le=1.0)
    trayectoria_profesional: str
    progresion_carrera: str

# Modelo para la comparación con los requisitos del puesto
class ComparisonResult(BaseModel):
    """Resultado de la comparación del CV con los requisitos del puesto"""
    job_description: str
    match_score: float = Field(ge=0.0, le=1.0)
    requisitos_cumplidos: List[str] = []
    requisitos_faltantes: List[str] = []
    habilidades_coincidentes: List[str] = []
    habilidades_faltantes: List[str] = []
    experiencia_relevante: str
    compatibilidad_cultural: Optional[float] = None
    observaciones: List[str] = []

# Modelo para la evaluación final
class FinalEvaluation(BaseModel):
    """Evaluación completa y recomendaciones finales"""
    cv_data: ClassifiedCV
    skills_evaluation: SkillsEvaluation
    experience_evaluation: ExperienceEvaluation
    comparison_result: ComparisonResult
    match_score: float = Field(ge=0.0, le=1.0)
    fortalezas: List[str] = []
    areas_mejora: List[str] = []
    recomendaciones: List[str] = []
    decision_sugerida: Literal["Contratar", "Considerar", "Rechazar"]
    justificacion: str
    resumen_visual: Dict[str, Any] = {} 