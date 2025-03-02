import logging
import google.generativeai as genai
from typing import Dict, Any, List
import os
import json

from pydantic import BaseModel

from .base_node import BaseNode
from ...models.node_schemas import ClassifiedCV, SkillsEvaluation, HabilidadEvaluada, NivelHabilidad, NivelRelevancia

# Configurar el logger
logger = logging.getLogger("cv_analyzer.nodes.skills_evaluator")

# Obtener API key desde variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

class SkillsEvaluatorInput(BaseModel):
    """Modelo para la entrada del evaluador de habilidades"""
    classified_cv: ClassifiedCV
    job_description: str

class SkillsEvaluatorNode(BaseNode[SkillsEvaluatorInput, SkillsEvaluation, Dict[str, Any]]):
    """Nodo responsable de evaluar habilidades técnicas y blandas del CV"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = None):
        super().__init__(name)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    async def process(self, input_data: SkillsEvaluatorInput, context: Dict[str, Any]) -> SkillsEvaluation:
        """Evalúa las habilidades técnicas y blandas utilizando Gemini AI"""
        classified_cv = input_data.classified_cv
        job_description = input_data.job_description
        
        logger.info(f"Evaluating skills from classified CV data")
        
        try:
            # Extraer las secciones relevantes para la evaluación de habilidades
            skills_text = classified_cv.habilidades_texto or ""
            experience_text = classified_cv.experiencia_texto or ""
            languages_text = classified_cv.idiomas_texto or ""
            
            # Crear el prompt para Gemini
            prompt = self._create_skills_evaluation_prompt(
                skills_text, 
                experience_text, 
                languages_text, 
                job_description
            )
            
            # Llamar a Gemini para evaluar las habilidades
            response = self.model.generate_content(prompt)
            
            # Procesar la respuesta
            skills_evaluation = self._process_gemini_response(response.text)
            
            logger.info(f"Successfully evaluated skills")
            
            return skills_evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating skills: {str(e)}")
            raise
    
    def _create_skills_evaluation_prompt(self, skills_text: str, experience_text: str, 
                                      languages_text: str, job_description: str) -> str:
        """Crea el prompt para la evaluación de habilidades"""
        return f"""
        Eres un asistente especializado en evaluación de habilidades en currículums.
        
        Necesito que evalúes las habilidades técnicas y blandas presentes en las siguientes secciones
        de un currículum, en relación con la descripción del puesto proporcionada.
        
        DESCRIPCIÓN DEL PUESTO:
        {job_description}
        
        SECCIÓN DE HABILIDADES DEL CV:
        {skills_text}
        
        SECCIÓN DE EXPERIENCIA DEL CV (para inferir habilidades adicionales):
        {experience_text}
        
        SECCIÓN DE IDIOMAS DEL CV:
        {languages_text}
        
        Por favor, realiza una evaluación detallada que incluya:
        1. Identificación de habilidades técnicas explícitas e implícitas
        2. Identificación de habilidades blandas
        3. Evaluación del nivel de cada habilidad (Básico, Intermedio, Avanzado, Experto)
        4. Evaluación de la relevancia de cada habilidad para el puesto (Baja, Media, Alta)
        5. Identificación de fortalezas y debilidades
        
        EVALUACIÓN DE COMPATIBILIDAD MÁS ESTRICTA:
        - Debes evaluar con mucha más rigurosidad si el candidato realmente tiene experiencia DIRECTA en el campo solicitado.
        - Valora muy alto (>0.8) SOLO a candidatos que hayan trabajado o estudiado en el campo ESPECÍFICO del puesto.
        - Candidatos de áreas no relacionadas deben recibir puntuaciones significativamente menores, incluso si tienen algunas habilidades transferibles.
        - Un candidato de RRHH para un puesto de RRHH debería tener una puntuación >0.8
        - Un candidato de Biología para un puesto de RRHH debería tener una puntuación <0.5
        - Un candidato de Programación para un puesto de RRHH debería tener una puntuación <0.4
        - La experiencia laboral DIRECTA en el campo cuenta 3 veces más que las habilidades transferibles.
        - La formación académica ESPECÍFICA en el campo cuenta 2 veces más que las habilidades relacionadas.
        - La experiencia relevante RECIENTE tiene más peso que la experiencia antigua.
        
        Devuelve SOLO un objeto JSON con el siguiente formato, sin explicaciones adicionales:
        {{
            "habilidades_tecnicas": [
                {{
                    "nombre": "Nombre de la habilidad técnica",
                    "nivel": "Nivel (Básico, Intermedio, Avanzado, Experto)",
                    "relevancia": "Relevancia para el puesto (Baja, Media, Alta)",
                    "descripcion": "Breve descripción o contexto de la habilidad",
                    "años_experiencia": 0.0
                }}
            ],
            "habilidades_blandas": [
                {{
                    "nombre": "Nombre de la habilidad blanda",
                    "nivel": "Nivel (Básico, Intermedio, Avanzado, Experto)",
                    "relevancia": "Relevancia para el puesto (Baja, Media, Alta)",
                    "descripcion": "Breve descripción o contexto de la habilidad"
                }}
            ],
            "idiomas": [
                {{
                    "idioma": "Nombre del idioma",
                    "nivel": "Nivel de competencia"
                }}
            ],
            "puntuacion_general": 0.0,
            "justificacion_puntuacion": "Explica brevemente cómo se calculó la puntuación general, considerando la relevancia de la experiencia y educación para el puesto específico",
            "campo_principal_candidato": "Identifica el campo principal de experiencia/educación del candidato (ej: RRHH, Programación, Marketing, etc.)",
            "campo_solicitado": "Identifica el campo principal que requiere el puesto según la descripción",
            "match_campo": true/false,
            "fortalezas": [
                "Descripción de fortaleza 1",
                "Descripción de fortaleza 2"
            ],
            "debilidades": [
                "Descripción de debilidad 1",
                "Descripción de debilidad 2"
            ]
        }}
        
        Asegúrate de que:
        - La puntuación general sea un número entre 0 y 1 que represente la calidad general de las habilidades en relación con el puesto.
        - Sea EXTREMADAMENTE estricto en la evaluación de compatibilidad. Solo candidatos con experiencia directa en el campo específico deben recibir puntuaciones altas.
        - Los niveles de habilidad sean uno de estos valores exactos: "Básico", "Intermedio", "Avanzado", "Experto"
        - Los niveles de relevancia sean uno de estos valores exactos: "Baja", "Media", "Alta"
        """
    
    def _process_gemini_response(self, response_text: str) -> SkillsEvaluation:
        """Procesa la respuesta de Gemini y la convierte en un objeto SkillsEvaluation"""
        try:
            # Limpiar la respuesta para obtener solo el JSON
            json_str = response_text
            
            # Si la respuesta contiene código markdown, extraer solo el JSON
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Parsear el JSON
            data = json.loads(json_str)
            
            # Convertir habilidades técnicas
            habilidades_tecnicas = []
            for skill_data in data.get("habilidades_tecnicas", []):
                try:
                    skill = HabilidadEvaluada(
                        nombre=skill_data["nombre"],
                        nivel=NivelHabilidad(skill_data["nivel"]),
                        relevancia=NivelRelevancia(skill_data["relevancia"]),
                        descripcion=skill_data.get("descripcion"),
                        años_experiencia=skill_data.get("años_experiencia")
                    )
                    habilidades_tecnicas.append(skill)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error processing technical skill: {e}. Skipping.")
            
            # Convertir habilidades blandas
            habilidades_blandas = []
            for skill_data in data.get("habilidades_blandas", []):
                try:
                    skill = HabilidadEvaluada(
                        nombre=skill_data["nombre"],
                        nivel=NivelHabilidad(skill_data["nivel"]),
                        relevancia=NivelRelevancia(skill_data["relevancia"]),
                        descripcion=skill_data.get("descripcion")
                    )
                    habilidades_blandas.append(skill)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error processing soft skill: {e}. Skipping.")
            
            # Crear el objeto SkillsEvaluation con los nuevos campos
            skills_evaluation = SkillsEvaluation(
                habilidades_tecnicas=habilidades_tecnicas,
                habilidades_blandas=habilidades_blandas,
                idiomas=data.get("idiomas", []),
                puntuacion_general=data.get("puntuacion_general", 0.5),
                justificacion_puntuacion=data.get("justificacion_puntuacion", ""),
                campo_principal_candidato=data.get("campo_principal_candidato", ""),
                campo_solicitado=data.get("campo_solicitado", ""),
                match_campo=data.get("match_campo", False),
                fortalezas=data.get("fortalezas", []),
                debilidades=data.get("debilidades", [])
            )
            
            return skills_evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from Gemini response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            raise 