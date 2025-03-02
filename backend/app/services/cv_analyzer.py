import os
import json
import fitz  # PyMuPDF
import google.generativeai as genai
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configurar el sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cv_analyzer")

# Cargar variables de entorno
load_dotenv()

# Configurar Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la clave API de Gemini en las variables de entorno")

genai.configure(api_key=GEMINI_API_KEY)

# Definir el modelo de Gemini a utilizar
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_text_from_pdf(file_path):
    """Extrae el texto de un archivo PDF usando PyMuPDF (fitz)."""
    logger.info(f"Iniciando extracción de texto del PDF: {os.path.basename(file_path)}")
    start_time = datetime.now()
    
    text = ""
    try:
        # Abrir el documento PDF
        doc = fitz.open(file_path)
        
        # Extraer texto de cada página
        total_pages = len(doc)
        logger.info(f"Procesando {total_pages} páginas del PDF")
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text + "\n\n"
            
        # Cerrar el documento
        doc.close()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Extracción de texto completada en {duration:.2f} segundos")
        
    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {str(e)}")
    
    return text

def generate_visual_summary(cv_text, job_description):
    """Genera un resumen visual del candidato usando Gemini."""
    logger.info("Iniciando generación del resumen visual con Gemini")
    start_time = datetime.now()
    
    prompt = f"""
    Eres un asistente especializado en recursos humanos.
    
    A continuación, te proporcionaré el texto extraído de un currículum y una descripción de puesto.
    Tu tarea es crear un resumen visual conciso del candidato y evaluar su compatibilidad con el puesto.
    
    Descripción del puesto:
    {job_description}
    
    Texto del currículum:
    {cv_text}
    
    Por favor, genera un resumen visual en formato JSON con la siguiente estructura:
    
    {{
        "perfil_candidato": "Un párrafo breve (máximo 3 frases) que describa al candidato, su experiencia y enfoque profesional",
        "compatibilidad_general": "Una frase que indique si el candidato es adecuado para el puesto y por qué",
        "nivel_compatibilidad": 0.0, // Un valor entre 0 y 1 que indique la compatibilidad
        "puntos_clave": [
            "Lista de 3-5 puntos clave sobre el candidato relevantes para el puesto"
        ],
        "habilidades_destacadas": [
            // 3-5 habilidades más relevantes para el puesto con su nivel de dominio
            {{
                "habilidad": "Nombre de la habilidad",
                "nivel": "Nivel de dominio (Básico, Intermedio, Avanzado, Experto)",
                "relevancia": "Alta/Media/Baja para el puesto"
            }}
        ],
        "experiencia_relevante": "Breve descripción de la experiencia más relevante para el puesto",
        "recomendacion_final": "Una recomendación clara sobre si contratar o no al candidato"
    }}
    
    Asegúrate de que el JSON sea válido y esté correctamente formateado.
    Devuelve SOLO el JSON, sin texto adicional.
    """
    
    try:
        logger.info("Enviando solicitud a Gemini para generar resumen visual")
        response = model.generate_content(prompt)
        
        # Extraer el JSON de la respuesta
        response_text = response.text
        
        # Limpiar el texto para asegurar que sea un JSON válido
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Convertir el texto a un diccionario
        result = json.loads(response_text)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Resumen visual generado con éxito en {duration:.2f} segundos")
        
        return result
    except Exception as e:
        logger.error(f"Error al generar el resumen visual con Gemini: {str(e)}")
        # En caso de error, devolver un resultado básico
        return {
            "perfil_candidato": "No se pudo generar un perfil del candidato",
            "compatibilidad_general": "No se pudo determinar la compatibilidad",
            "nivel_compatibilidad": 0.5,
            "puntos_clave": ["No se pudieron extraer puntos clave"],
            "habilidades_destacadas": [],
            "experiencia_relevante": "No se pudo extraer la experiencia relevante",
            "recomendacion_final": "Se requiere revisión manual del CV"
        }

def analyze_cv_with_gemini(cv_text, job_description):
    """Analiza el CV usando Gemini API."""
    logger.info("Iniciando análisis completo del CV con Gemini")
    start_time = datetime.now()
    
    prompt = f"""
    Eres un asistente especializado en analizar currículums. 
    
    A continuación, te proporcionaré el texto extraído de un currículum y una descripción de puesto.
    Tu tarea es analizar el currículum y extraer la información relevante en un formato estructurado.
    
    Descripción del puesto:
    {job_description}
    
    Texto del currículum:
    {cv_text}
    
    Por favor, extrae la siguiente información del currículum y devuélvela en formato JSON:
    
    {{
        "cv_data": {{
            "nombre": "Nombre completo del candidato",
            "correo": "Correo electrónico del candidato",
            "telefono": "Número de teléfono del candidato",
            "ubicacion": "Ubicación del candidato (ciudad, país)",
            "linkedin": "Perfil de LinkedIn (si está disponible)",
            "resumen": "Resumen o perfil profesional del candidato",
            "educacion": [
                {{
                    "institucion": "Nombre de la institución educativa",
                    "titulo": "Título obtenido",
                    "campo": "Campo de estudio",
                    "fecha_inicio": "Fecha de inicio (YYYY-MM o YYYY)",
                    "fecha_fin": "Fecha de finalización (YYYY-MM o YYYY, o 'Presente')",
                    "descripcion": "Descripción adicional (opcional)"
                }}
            ],
            "experiencia": [
                {{
                    "empresa": "Nombre de la empresa",
                    "puesto": "Título del puesto",
                    "fecha_inicio": "Fecha de inicio (YYYY-MM o YYYY)",
                    "fecha_fin": "Fecha de finalización (YYYY-MM o YYYY, o 'Presente')",
                    "ubicacion": "Ubicación del trabajo",
                    "descripcion": "Descripción de responsabilidades y logros",
                    "tecnologias": ["Lista de tecnologías utilizadas"]
                }}
            ],
            "habilidades_tecnicas": ["Lista de habilidades técnicas"],
            "habilidades_blandas": ["Lista de habilidades blandas o soft skills"],
            "idiomas": [
                {{
                    "idioma": "Nombre del idioma",
                    "nivel": "Nivel de competencia (Básico, Intermedio, Avanzado, Nativo)"
                }}
            ],
            "certificaciones": [
                {{
                    "nombre": "Nombre de la certificación",
                    "emisor": "Entidad emisora",
                    "fecha": "Fecha de obtención",
                    "expiracion": "Fecha de expiración (si aplica)"
                }}
            ],
            "proyectos": [
                {{
                    "nombre": "Nombre del proyecto",
                    "descripcion": "Descripción del proyecto",
                    "tecnologias": ["Tecnologías utilizadas"],
                    "url": "URL del proyecto (si está disponible)"
                }}
            ],
            "logros": ["Lista de logros relevantes"],
            "intereses": ["Lista de intereses personales o profesionales"],
            "referencias": [
                {{
                    "nombre": "Nombre de la referencia",
                    "relacion": "Relación profesional",
                    "empresa": "Empresa",
                    "contacto": "Información de contacto (si está disponible)"
                }}
            ]
        }},
        "match_score": 0.0, // Puntuación de 0 a 1 que indica la compatibilidad con el puesto
        "fortalezas": ["Lista de fortalezas del candidato para el puesto"],
        "areas_mejora": ["Áreas donde el candidato podría mejorar para el puesto"],
        "recomendaciones": ["Recomendaciones para el candidato"]
    }}
    
    Notas importantes:
    1. Si alguna información no está disponible en el CV, deja el campo como null o un array vacío según corresponda.
    2. Asegúrate de que el JSON sea válido y esté correctamente formateado.
    3. Basa tu análisis en la comparación entre las habilidades y experiencia del candidato y los requisitos del puesto.
    4. Sé objetivo en tu evaluación.
    
    Devuelve SOLO el JSON, sin texto adicional.
    """
    
    try:
        logger.info("Enviando solicitud a Gemini para análisis completo del CV")
        response = model.generate_content(prompt)
        
        # Extraer el JSON de la respuesta
        response_text = response.text
        
        # Limpiar el texto para asegurar que sea un JSON válido
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Convertir el texto a un diccionario
        result = json.loads(response_text)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Análisis completo del CV generado con éxito en {duration:.2f} segundos")
        
        return result
    except Exception as e:
        logger.error(f"Error al analizar el CV con Gemini: {str(e)}")
        # En caso de error, devolver un resultado básico
        return {
            "status": "error",
            "message": f"Error al analizar el CV: {str(e)}",
            "cv_text_length": len(cv_text),
            "job_description_length": len(job_description)
        } 