import os
import logging
from typing import Dict, Any
import asyncio
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno antes de importar los nodos
load_dotenv()

from ..models.node_schemas import (
    FinalEvaluation, 
    CVDocument,
    ClassifiedCV,
    SkillsEvaluation,
    ExperienceEvaluation,
    ComparisonResult
)
from ..models.schemas import AnalysisResult, CVData

from .nodes import (
    WorkflowManager,
    ExtractorNode,
    ExtractorInput,
    ClassifierNode,
    SkillsEvaluatorNode,
    SkillsEvaluatorInput
)

# Configurar el logger
logger = logging.getLogger("cv_analyzer.workflow_service")

class CVAnalyzerWorkflowService:
    """Servicio que orquesta el flujo de trabajo para el análisis de CV"""
    
    def __init__(self):
        # Inicializar los nodos
        self.extractor_node = ExtractorNode()
        self.classifier_node = ClassifierNode()
        self.skills_evaluator_node = SkillsEvaluatorNode()
        
        # Configurar el gestor de flujo de trabajo
        self.workflow_manager = WorkflowManager("CVAnalysisWorkflow")
        
        # Añadir nodos al flujo de trabajo
        self.workflow_manager.add_node(self.extractor_node)
        self.workflow_manager.add_node(self.classifier_node)
        self.workflow_manager.add_node(self.skills_evaluator_node)
        
        # Definir el flujo de trabajo
        self.workflow_manager.connect(self.extractor_node, self.classifier_node)
        # Nota: Ya no conectamos classifier_node con skills_evaluator_node directamente
        # porque manejaremos esta transición manualmente en el método analyze_cv
        
        logger.info("CV Analyzer Workflow Service initialized")
    
    async def analyze_cv(self, file_path: str, job_description: str) -> AnalysisResult:
        """Analiza un CV utilizando el flujo de trabajo configurado"""
        start_time = datetime.now()
        logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting CV analysis for file: {file_path}")
        
        try:
            # Preparar el contexto del flujo de trabajo
            workflow_context = {
                "job_description": job_description,
                "file_path": file_path,
                "filename": os.path.basename(file_path)
            }
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Contexto de flujo de trabajo preparado para archivo: {os.path.basename(file_path)}")
            
            # Preparar la entrada para el nodo inicial (extractor)
            extractor_input = ExtractorInput(
                file_path=file_path
            )
            
            # Ejecutar el flujo de trabajo inicial (Extractor -> Clasificador)
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando ejecución del flujo Extractor -> Clasificador")
            extractor_start_time = datetime.now()
            results = await self.workflow_manager.execute(
                start_node=self.extractor_node.name,
                initial_input=extractor_input,
                context=workflow_context
            )
            extractor_end_time = datetime.now()
            extractor_duration = (extractor_end_time - extractor_start_time).total_seconds()
            logger.info(f"[{extractor_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Flujo Extractor -> Clasificador completado en {extractor_duration:.2f} segundos")
            
            # Obtener resultados intermedios
            cv_document: CVDocument = results.get(self.extractor_node.name)
            classified_cv: ClassifiedCV = results.get(self.classifier_node.name)
            
            # Preparar entrada para el evaluador de habilidades
            skills_evaluator_input = SkillsEvaluatorInput(
                classified_cv=classified_cv,
                job_description=job_description
            )
            
            # Ejecutar el nodo de evaluación de habilidades
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando evaluación de habilidades")
            skills_start_time = datetime.now()
            skills_evaluation, _ = await self.skills_evaluator_node.execute(
                skills_evaluator_input, 
                workflow_context
            )
            skills_end_time = datetime.now()
            skills_duration = (skills_end_time - skills_start_time).total_seconds()
            logger.info(f"[{skills_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Evaluación de habilidades completada en {skills_duration:.2f} segundos")
            
            # Crear el conjunto completo de resultados
            results[self.skills_evaluator_node.name] = skills_evaluation
            
            # Convertir a AnalysisResult para compatibilidad con la API actual
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generando resultado final del análisis")
            conversion_start_time = datetime.now()
            analysis_result = self._convert_to_analysis_result(
                classified_cv, 
                skills_evaluation, 
                job_description
            )
            conversion_end_time = datetime.now()
            conversion_duration = (conversion_end_time - conversion_start_time).total_seconds()
            logger.info(f"[{conversion_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Resultado final generado en {conversion_duration:.2f} segundos")
            
            # Calcular tiempo total
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            logger.info(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] CV analysis completed successfully for file: {file_path} in {total_duration:.2f} seconds")
            
            # Registrar información sobre el resultado
            match_score = analysis_result.match_score if hasattr(analysis_result, 'match_score') else 0.0
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Puntuación final de compatibilidad: {match_score:.2f}")
            
            return analysis_result
            
        except Exception as e:
            error_time = datetime.now()
            logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] Error analyzing CV: {str(e)}")
            raise
    
    def _convert_to_analysis_result(self, 
                                   classified_cv: ClassifiedCV, 
                                   skills_evaluation: SkillsEvaluation,
                                   job_description: str) -> AnalysisResult:
        """Convierte los resultados de los nodos al formato AnalysisResult para la API"""
        # Convertir ClassifiedCV a CVData
        cv_data = CVData(
            nombre=classified_cv.nombre,
            correo=classified_cv.correo,
            telefono=classified_cv.telefono,
            ubicacion=classified_cv.ubicacion,
            linkedin=classified_cv.linkedin,
            resumen=classified_cv.resumen,
            habilidades_tecnicas=[skill.nombre for skill in skills_evaluation.habilidades_tecnicas],
            habilidades_blandas=[skill.nombre for skill in skills_evaluation.habilidades_blandas],
            idiomas=skills_evaluation.idiomas
        )
        
        # Generar el resumen visual (simplificado por ahora)
        resumen_visual = {
            "perfil_candidato": classified_cv.resumen or "Perfil no disponible",
            "compatibilidad_general": skills_evaluation.justificacion_puntuacion or "Evaluación preliminar basada en habilidades",
            "nivel_compatibilidad": skills_evaluation.puntuacion_general,
            "campo_candidato": skills_evaluation.campo_principal_candidato,
            "campo_solicitado": skills_evaluation.campo_solicitado,
            "match_campo": skills_evaluation.match_campo,
            "puntos_clave": skills_evaluation.fortalezas[:3],
            "habilidades_destacadas": [
                {
                    "habilidad": skill.nombre,
                    "nivel": skill.nivel.value,
                    "relevancia": skill.relevancia.value
                }
                for skill in sorted(
                    skills_evaluation.habilidades_tecnicas, 
                    key=lambda x: (
                        0 if x.relevancia.value == "Alta" else 
                        1 if x.relevancia.value == "Media" else 2
                    )
                )[:5]
            ],
            "experiencia_relevante": "Pendiente de evaluación detallada",
            "recomendacion_final": "Se recomienda continuar con el proceso de evaluación"
        }
        
        # Crear y devolver el resultado del análisis
        return AnalysisResult(
            cv_data=cv_data,
            match_score=skills_evaluation.puntuacion_general,
            fortalezas=skills_evaluation.fortalezas,
            areas_mejora=skills_evaluation.debilidades,
            justificacion_puntuacion=skills_evaluation.justificacion_puntuacion,
            campo_principal_candidato=skills_evaluation.campo_principal_candidato,
            campo_solicitado=skills_evaluation.campo_solicitado, 
            match_campo=skills_evaluation.match_campo,
            recomendaciones=[
                "Recomendación basada en análisis preliminar de habilidades",
                "Se recomienda revisar la experiencia laboral con más detalle",
                "Pendiente de análisis completo con todos los nodos"
            ],
            resumen_visual=resumen_visual
        )
    
    def clear_caches(self):
        """Limpia todas las cachés de todos los nodos"""
        self.workflow_manager.clear_all_caches()
        logger.info("All caches cleared")
    
    def get_workflow_status(self):
        """Obtiene el estado actual del flujo de trabajo"""
        return self.workflow_manager.get_status()
    
    def get_workflow_metadata(self):
        """Obtiene los metadatos de la última ejecución del flujo de trabajo"""
        return self.workflow_manager.get_last_metadata() 