from pydantic import BaseModel
from typing import Dict, List, Optional, Any

# Definir la estructura de datos para el CV analizado
class CVData(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    ubicacion: Optional[str] = None
    linkedin: Optional[str] = None
    resumen: Optional[str] = None
    educacion: List[Dict[str, Any]] = []
    experiencia: List[Dict[str, Any]] = []
    habilidades_tecnicas: List[str] = []
    habilidades_blandas: List[str] = []
    idiomas: List[Dict[str, str]] = []
    certificaciones: List[Dict[str, Any]] = []
    proyectos: List[Dict[str, Any]] = []
    logros: List[str] = []
    intereses: List[str] = []
    referencias: List[Dict[str, Any]] = []

class AnalysisResult(BaseModel):
    cv_data: CVData
    match_score: float
    fortalezas: List[str]
    areas_mejora: List[str]
    recomendaciones: List[str]
    justificacion_puntuacion: Optional[str] = None
    campo_principal_candidato: Optional[str] = None
    campo_solicitado: Optional[str] = None
    match_campo: bool = False
    resumen_visual: Dict[str, Any] = {} 