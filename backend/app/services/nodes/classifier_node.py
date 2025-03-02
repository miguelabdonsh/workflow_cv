import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import os
import json

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
        
        logger.info(f"Classifying CV text ({len(cv_text)} characters)")
        
        try:
            # Crear el prompt para Gemini
            prompt = self._create_classification_prompt(cv_text)
            
            # Llamar a Gemini para clasificar el texto
            response = self.model.generate_content(prompt)
            
            # Procesar la respuesta
            classified_cv = self._process_gemini_response(response.text)
            
            logger.info(f"Successfully classified CV into sections")
            
            return classified_cv
            
        except Exception as e:
            logger.error(f"Error classifying CV: {str(e)}")
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