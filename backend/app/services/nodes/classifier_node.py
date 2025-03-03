import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime

from pydantic import BaseModel

from .base_node import BaseNode
from ...models.node_schemas import CVDocument, ClassifiedCV

# Configurar el logger
logger = logging.getLogger("cv_analyzer.nodes.classifier")

# Obtener API key desde variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

class ClassifierNode(BaseNode[CVDocument, ClassifiedCV, Dict[str, Any]]):
    """Nodo responsable de clasificar y estructurar las secciones del CV"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = None):
        super().__init__(name)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    async def process(self, input_data: CVDocument, context: Dict[str, Any]) -> ClassifiedCV:
        """Clasifica el texto del CV en secciones utilizando Gemini AI"""
        cv_text = input_data.text
        start_time = datetime.now()
        
        logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Classifying CV text ({len(cv_text)} characters)")
        
        try:
            # Crear el prompt para Gemini
            prompt_start_time = datetime.now()
            prompt = self._create_classification_prompt(cv_text)
            prompt_end_time = datetime.now()
            prompt_duration = (prompt_end_time - prompt_start_time).total_seconds()
            logger.info(f"[{prompt_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Prompt para clasificación generado en {prompt_duration:.2f} segundos")
            
            # Llamar a Gemini para clasificar el CV
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enviando solicitud a Gemini para clasificación")
            gemini_start_time = datetime.now()
            response = self.model.generate_content(prompt)
            gemini_end_time = datetime.now()
            gemini_duration = (gemini_end_time - gemini_start_time).total_seconds()
            logger.info(f"[{gemini_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Respuesta de Gemini recibida en {gemini_duration:.2f} segundos")
            
            # Procesar la respuesta
            processing_start_time = datetime.now()
            classified_cv = self._process_gemini_response(response.text)
            processing_end_time = datetime.now()
            processing_duration = (processing_end_time - processing_start_time).total_seconds()
            logger.info(f"[{processing_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Respuesta procesada en {processing_duration:.2f} segundos")
            
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            logger.info(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully classified CV into sections in {total_duration:.2f} seconds")
            
            # Registrar información sobre las secciones encontradas
            sections_found = []
            if classified_cv.nombre: sections_found.append("nombre")
            if classified_cv.correo: sections_found.append("correo")
            if classified_cv.telefono: sections_found.append("telefono")
            if classified_cv.ubicacion: sections_found.append("ubicacion")
            if classified_cv.linkedin: sections_found.append("linkedin")
            if classified_cv.resumen: sections_found.append("resumen")
            if classified_cv.educacion_texto: sections_found.append("educacion")
            if classified_cv.experiencia_texto: sections_found.append("experiencia")
            if classified_cv.habilidades_texto: sections_found.append("habilidades")
            if classified_cv.idiomas_texto: sections_found.append("idiomas")
            
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Secciones encontradas: {', '.join(sections_found)}")
            
            return classified_cv
            
        except Exception as e:
            error_time = datetime.now()
            logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] Error classifying CV: {str(e)}")
            raise
    
    def _create_classification_prompt(self, cv_text: str) -> str:
        """Crea el prompt para la clasificación del CV"""
        return f"""
        Eres un asistente especializado en análisis de currículums.
        
        Necesito que identifiques y extraigas las diferentes secciones del siguiente currículum.
        
        Texto del currículum:
        {cv_text}
        
        Por favor, clasifica el texto en las siguientes secciones (si están presentes):
        1. Información personal (nombre, correo, teléfono, ubicación, LinkedIn)
        2. Resumen o perfil profesional
        3. Educación
        4. Experiencia laboral
        5. Habilidades técnicas
        6. Habilidades blandas
        7. Idiomas
        8. Certificaciones
        9. Proyectos
        10. Logros
        11. Intereses
        12. Referencias
        
        Para cada sección, extrae el texto completo correspondiente. Si alguna sección no está presente en el CV, déjala como null.
        
        Devuelve SOLO un objeto JSON con el siguiente formato, sin explicaciones adicionales:
        {{
            "nombre": "Nombre completo de la persona",
            "correo": "email@example.com",
            "telefono": "Número de teléfono",
            "ubicacion": "Ciudad, País",
            "linkedin": "URL de LinkedIn (si está disponible)",
            "resumen": "Texto del resumen o perfil profesional",
            "educacion_texto": "Texto completo de la sección de educación",
            "experiencia_texto": "Texto completo de la sección de experiencia laboral",
            "habilidades_texto": "Texto de la sección de habilidades técnicas",
            "habilidades_blandas_texto": "Texto de la sección de habilidades blandas",
            "idiomas_texto": "Texto de la sección de idiomas",
            "certificaciones_texto": "Texto de la sección de certificaciones",
            "proyectos_texto": "Texto de la sección de proyectos",
            "logros_texto": "Texto de la sección de logros",
            "intereses_texto": "Texto de la sección de intereses",
            "referencias_texto": "Texto de la sección de referencias",
            "secciones_adicionales": {{
                "nombre_seccion": "texto de la sección"
            }}
        }}
        """
    
    def _process_gemini_response(self, response_text: str) -> ClassifiedCV:
        """Procesa la respuesta de Gemini y la convierte en un objeto ClassifiedCV"""
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
            
            # Crear el objeto ClassifiedCV
            classified_cv = ClassifiedCV(
                nombre=data.get("nombre"),
                correo=data.get("correo"),
                telefono=data.get("telefono"),
                ubicacion=data.get("ubicacion"),
                linkedin=data.get("linkedin"),
                resumen=data.get("resumen"),
                educacion_texto=data.get("educacion_texto"),
                experiencia_texto=data.get("experiencia_texto"),
                habilidades_texto=data.get("habilidades_texto") or data.get("habilidades_tecnicas_texto"),
                idiomas_texto=data.get("idiomas_texto"),
                certificaciones_texto=data.get("certificaciones_texto"),
                proyectos_texto=data.get("proyectos_texto"),
                logros_texto=data.get("logros_texto"),
                intereses_texto=data.get("intereses_texto"),
                referencias_texto=data.get("referencias_texto")
            )
            
            # Añadir secciones adicionales si existen
            additional_sections = data.get("secciones_adicionales", {})
            if isinstance(additional_sections, dict):
                classified_cv.secciones_adicionales = additional_sections
            
            return classified_cv
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from Gemini response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            raise 