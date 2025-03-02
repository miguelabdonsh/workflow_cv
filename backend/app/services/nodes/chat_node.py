import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import os
import json
from pydantic import BaseModel, Field
from datetime import datetime

from .base_node import BaseNode

# Configurar el logger
logger = logging.getLogger("cv_analyzer.nodes.chat")

# Obtener API key desde variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

class ChatMessage(BaseModel):
    """Modelo para representar un mensaje en la conversación"""
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    """Modelo para representar una sesión de chat"""
    session_id: str
    messages: List[ChatMessage] = []
    cv_name: Optional[str] = None
    cv_match_score: Optional[float] = None
    cv_data: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None
    skills_evaluation: Optional[Dict[str, Any]] = None
    # Nuevo campo para soportar múltiples CVs
    multiple_cvs: Optional[List[Dict[str, Any]]] = None
    is_multi_cv_session: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ChatInput(BaseModel):
    """Modelo para la entrada del nodo de chat"""
    session_id: str
    message: str
    job_description: Optional[str] = None
    cv_data: Optional[Dict[str, Any]] = None
    skills_evaluation: Optional[Dict[str, Any]] = None
    # Nuevo campo para la entrada con múltiples CVs
    multiple_cvs: Optional[List[Dict[str, Any]]] = None
    is_multi_cv_session: bool = False

class ChatOutput(BaseModel):
    """Modelo para la salida del nodo de chat"""
    response: str
    session_id: str

class ChatNode(BaseNode[ChatInput, ChatOutput, Dict[str, Any]]):
    """Nodo para gestionar conversaciones de chat sobre un CV"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = None):
        super().__init__(name or "ChatNode")
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.sessions: Dict[str, ChatSession] = {}
        logger.info(f"ChatNode initialized with model: {model_name}")
    
    async def process(self, input_data: ChatInput, context: Dict[str, Any]) -> ChatOutput:
        """Procesa un mensaje de chat y genera una respuesta"""
        session_id = input_data.session_id
        message = input_data.message
        
        logger.info(f"Processing chat message for session: {session_id}")
        
        try:
            # Obtener o crear la sesión
            session = self.get_session(session_id)
            if not session:
                # Si la sesión no existe, crearla
                session = self.create_session(
                    session_id=session_id,
                    cv_data=input_data.cv_data,
                    job_description=input_data.job_description,
                    multiple_cvs=input_data.multiple_cvs,
                    is_multi_cv_session=input_data.is_multi_cv_session
                )
            
            # Añadir el mensaje del usuario a la sesión
            session.messages.append(
                ChatMessage(
                    role="user",
                    content=message
                )
            )
            session.updated_at = datetime.now()
            
            # Generar prompt para el modelo
            prompt = self._create_chat_prompt(session)
            
            # Llamar al modelo para generar la respuesta
            response = self.model.generate_content(prompt)
            
            # Extraer la respuesta generada
            generated_response = response.text
            
            # Añadir la respuesta a la sesión
            session.messages.append(
                ChatMessage(
                    role="assistant",
                    content=generated_response
                )
            )
            
            # Actualizar la sesión
            self.sessions[session_id] = session
            
            logger.info(f"Generated response for session: {session_id}")
            
            # Devolver la respuesta
            return ChatOutput(
                response=generated_response,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            raise
    
    def _create_chat_prompt(self, session: ChatSession) -> str:
        """Crea el prompt para el modelo de chat basado en el historial de la sesión"""
        
        # Generar diferente prompt según sea una sesión de CV único o múltiple
        if session.is_multi_cv_session and session.multiple_cvs:
            # Prompt para múltiples CVs
            cv_summaries = []
            for idx, cv in enumerate(session.multiple_cvs):
                cv_data = cv.get("cv_data", {})
                nombre = cv_data.get("nombre", f"Candidato {idx+1}")
                match_score = cv.get("match_score", 0)
                fortalezas = cv.get("fortalezas", [])
                areas_mejora = cv.get("areas_mejora", [])
                
                # Crear resumen para este CV
                cv_summary = f"""
                --- CANDIDATO {idx+1}: {nombre} ---
                Puntuación de compatibilidad: {match_score * 100:.0f}%
                
                Fortalezas principales:
                {' '.join(['- ' + f for f in fortalezas[:3]])}
                
                Áreas de mejora:
                {' '.join(['- ' + a for a in areas_mejora[:3]])}
                
                Información personal:
                - Email: {cv_data.get('correo', 'No disponible')}
                - Ubicación: {cv_data.get('ubicacion', 'No disponible')}
                - Teléfono: {cv_data.get('telefono', 'No disponible')}
                
                Habilidades técnicas: {', '.join(cv_data.get('habilidades_tecnicas', [])[:5])}
                
                Idiomas: {', '.join([f"{i.get('idioma', '')}: {i.get('nivel', '')}" for i in cv_data.get('idiomas', [])[:3]])}
                """
                cv_summaries.append(cv_summary)
            
            # Crear el prompt completo
            system_prompt = f"""
            Eres un asistente especializado en recursos humanos y análisis de currículums.
            
            Tienes acceso a los datos de {len(session.multiple_cvs)} candidatos que han sido evaluados para un puesto.
            
            Descripción del puesto:
            {session.job_description or "No disponible"}
            
            INFORMACIÓN DE LOS CANDIDATOS:
            
            {' '.join(cv_summaries)}
            
            Tu tarea es responder preguntas sobre estos candidatos, comparar sus perfiles, 
            identificar al más adecuado para el puesto según sus habilidades y experiencia,
            y proporcionar consejos para la selección.
            
            Recuerda que puedes comparar a los candidatos entre sí cuando te lo soliciten,
            pero evita hacer juicios innecesariamente negativos sobre cualquiera de ellos.
            
            HISTORIAL DE LA CONVERSACIÓN:
            """
        else:
            # Prompt original para un solo CV
            cv_data = session.cv_data or {}
            nombre = cv_data.get("nombre", "este candidato")
            
            system_prompt = f"""
            Eres un asistente especializado en recursos humanos y análisis de currículums.
            
            Estás analizando el CV de {nombre}.
            
            Información del candidato:
            - Nombre: {cv_data.get('nombre', 'No disponible')}
            - Email: {cv_data.get('correo', 'No disponible')}
            - Ubicación: {cv_data.get('ubicacion', 'No disponible')}
            - Teléfono: {cv_data.get('telefono', 'No disponible')}
            - Resumen: {cv_data.get('resumen', 'No disponible')}
            
            Habilidades técnicas: {', '.join(cv_data.get('habilidades_tecnicas', []))}
            
            Habilidades blandas: {', '.join(cv_data.get('habilidades_blandas', []))}
            
            Idiomas: {', '.join([f"{i.get('idioma', '')}: {i.get('nivel', '')}" for i in cv_data.get('idiomas', [])])}
            
            Descripción del puesto:
            {session.job_description or "No disponible"}
            
            HISTORIAL DE LA CONVERSACIÓN:
            """
        
        # Añadir el historial de mensajes
        for message in session.messages:
            if message.role == "user":
                system_prompt += f"\nUsuario: {message.content}"
            else:
                system_prompt += f"\nAsistente: {message.content}"
        
        # Añadir el indicador para la próxima respuesta
        system_prompt += "\nAsistente:"
        
        return system_prompt
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Obtiene una sesión de chat por su ID"""
        return self.sessions.get(session_id)
    
    def create_session(self, session_id: str, cv_name: Optional[str] = None, 
                  cv_data: Optional[Dict[str, Any]] = None, 
                  job_description: Optional[str] = None,
                  skills_evaluation: Optional[Dict[str, Any]] = None,
                  multiple_cvs: Optional[List[Dict[str, Any]]] = None,
                  is_multi_cv_session: bool = False) -> ChatSession:
        """Crea una nueva sesión de chat"""
        session = ChatSession(
            session_id=session_id,
            cv_name=cv_name,
            cv_data=cv_data,
            job_description=job_description,
            skills_evaluation=skills_evaluation,
            multiple_cvs=multiple_cvs,
            is_multi_cv_session=is_multi_cv_session
        )
        self.sessions[session_id] = session
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión de chat"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False 