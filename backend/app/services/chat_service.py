import logging
from typing import Dict, Any, Optional, List
import uuid

from .nodes.chat_node import ChatNode, ChatInput, ChatSession

# Configurar el logger
logger = logging.getLogger("cv_analyzer.services.chat")

class ChatService:
    """Servicio para gestionar las conversaciones de chat"""
    
    def __init__(self):
        # Inicializar el nodo de chat
        self.chat_node = ChatNode()
        # Mantener un registro de los datos del CV para cada sesión
        self.session_data = {}
        logger.info("Servicio de chat inicializado")
    
    def create_session(self, session_id: str, cv_data: Optional[Dict[str, Any]] = None, 
                      job_description: Optional[str] = None) -> Dict[str, Any]:
        """Crea una nueva sesión de chat para un solo CV"""
        try:
            # Almacenar los datos del CV y la descripción del trabajo para esta sesión
            if cv_data or job_description:
                self.session_data[session_id] = {
                    "cv_data": cv_data,
                    "job_description": job_description
                }
                logger.info(f"Datos de sesión almacenados para: {session_id}")
            
            # Extraer el nombre del candidato de los datos del CV, si está disponible
            cv_name = None
            if cv_data and "nombre" in cv_data:
                cv_name = cv_data.get("nombre")
            
            # Crear la sesión con todos los datos disponibles
            session = self.chat_node.create_session(
                session_id=session_id, 
                cv_name=cv_name,
                cv_data=cv_data,
                job_description=job_description
            )
            
            # Devolver información básica de la sesión
            return {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "cv_name": session.cv_name
            }
        
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    def create_multi_cv_session(self, session_id: str, results: List[Dict[str, Any]], 
                              job_description: Optional[str] = None) -> Dict[str, Any]:
        """Crea una nueva sesión de chat para múltiples CVs"""
        try:
            # Almacenar los datos de múltiples CVs y la descripción del trabajo para esta sesión
            self.session_data[session_id] = {
                "multiple_cvs": results,
                "job_description": job_description,
                "is_multi_cv_session": True
            }
            logger.info(f"Datos de sesión múltiple almacenados para: {session_id}")
            
            # Crear la sesión con todos los datos disponibles
            session = self.chat_node.create_session(
                session_id=session_id,
                job_description=job_description,
                multiple_cvs=results,
                is_multi_cv_session=True
            )
            
            # Devolver información básica de la sesión
            return {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "is_multi_cv_session": True,
                "candidate_count": len(results)
            }
        
        except Exception as e:
            logger.error(f"Error creating multi-CV chat session: {str(e)}")
            raise
    
    async def process_message(self, session_id: str, message: str) -> str:
        """Procesa un mensaje del usuario y devuelve la respuesta"""
        try:
            # Obtener la sesión
            session = self.chat_node.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # Recuperar los datos asociados con esta sesión
            session_data = self.session_data.get(session_id, {})
            
            # Crear la entrada para el nodo de chat según el tipo de sesión
            if session_data.get("is_multi_cv_session", False):
                # Sesión para múltiples CVs
                input_data = ChatInput(
                    session_id=session_id,
                    message=message,
                    job_description=session_data.get("job_description"),
                    multiple_cvs=session_data.get("multiple_cvs"),
                    is_multi_cv_session=True
                )
            else:
                # Sesión para un solo CV
                input_data = ChatInput(
                    session_id=session_id,
                    message=message,
                    cv_data=session_data.get("cv_data"),
                    job_description=session_data.get("job_description")
                )
            
            # Procesar el mensaje con el nodo de chat
            result = await self.chat_node.execute(input_data, {})
            
            # Devolver la respuesta
            return result[0].response
        
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            raise
    
    def session_exists(self, session_id: str) -> bool:
        """Verifica si existe una sesión de chat"""
        return self.chat_node.get_session(session_id) is not None
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Obtiene información sobre una sesión de chat"""
        session = self.chat_node.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Extraer mensajes recientes
        messages = []
        for msg in session.messages[-10:]:  # Últimos 10 mensajes
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })
        
        # Devolver información de la sesión
        session_info = {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
            "recent_messages": messages
        }
        
        # Añadir información específica según el tipo de sesión
        if session.is_multi_cv_session:
            session_info["is_multi_cv_session"] = True
            session_info["candidate_count"] = len(session.multiple_cvs) if session.multiple_cvs else 0
        else:
            session_info["cv_name"] = session.cv_name
        
        return session_info
    
    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión de chat"""
        # Eliminar los datos de la sesión
        if session_id in self.session_data:
            del self.session_data[session_id]
            logger.info(f"Datos de sesión eliminados para: {session_id}")
        
        # Eliminar la sesión del nodo de chat
        return self.chat_node.delete_session(session_id)
    
    def clear_sessions(self):
        """Limpia todas las sesiones de chat"""
        self.session_data = {}
        self.chat_node.clear_cache()
        return True 