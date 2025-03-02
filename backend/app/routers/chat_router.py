from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import uuid

from ..services.chat_service import ChatService

# Configurar el logger
logger = logging.getLogger("cv_analyzer.chat")

router = APIRouter()

# Instancia del servicio de chat
chat_service = ChatService()

class ChatSessionRequest(BaseModel):
    """Modelo para solicitar una nueva sesión de chat"""
    cv_id: Optional[str] = None
    cv_data: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None

class MultiCVChatSessionRequest(BaseModel):
    """Modelo para solicitar una nueva sesión de chat con múltiples CVs"""
    results: List[Dict[str, Any]]
    job_description: Optional[str] = None

class ChatMessageRequest(BaseModel):
    """Modelo para enviar un mensaje de chat"""
    session_id: str
    message: str

class ChatResponse(BaseModel):
    """Modelo para la respuesta del chat"""
    session_id: str
    response: str
    
@router.post("/chat/sessions/")
async def create_chat_session(request: ChatSessionRequest):
    """Crea una nueva sesión de chat"""
    try:
        session_id = str(uuid.uuid4())
        
        # Crear una nueva sesión
        session = chat_service.create_session(
            session_id=session_id, 
            cv_data=request.cv_data,
            job_description=request.job_description
        )
        
        logger.info(f"Nueva sesión de chat creada: {session_id}")
        
        return {"session_id": session_id, "message": "Sesión de chat creada correctamente"}
    
    except Exception as e:
        logger.error(f"Error al crear sesión de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear sesión de chat: {str(e)}")

@router.post("/chat/multi-sessions/")
async def create_multi_cv_chat_session(request: MultiCVChatSessionRequest):
    """Crea una nueva sesión de chat para múltiples CVs"""
    try:
        session_id = str(uuid.uuid4())
        
        # Crear una nueva sesión para múltiples CVs
        session = chat_service.create_multi_cv_session(
            session_id=session_id, 
            results=request.results,
            job_description=request.job_description
        )
        
        logger.info(f"Nueva sesión de chat multi-CV creada: {session_id} con {len(request.results)} candidatos")
        
        return {
            "session_id": session_id, 
            "message": "Sesión de chat multi-CV creada correctamente",
            "candidate_count": len(request.results)
        }
    
    except Exception as e:
        logger.error(f"Error al crear sesión de chat multi-CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear sesión de chat multi-CV: {str(e)}")

@router.post("/chat/messages/")
async def send_chat_message(request: ChatMessageRequest):
    """Envía un mensaje a la sesión de chat y obtiene una respuesta"""
    try:
        session_id = request.session_id
        message = request.message
        
        logger.info(f"Mensaje recibido para sesión {session_id}: {message[:50]}...")
        
        # Verificar que la sesión existe
        if not chat_service.session_exists(session_id):
            logger.warning(f"Sesión de chat no encontrada: {session_id}")
            raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
        
        # Procesar el mensaje y obtener la respuesta
        response = await chat_service.process_message(session_id, message)
        
        return ChatResponse(
            session_id=session_id,
            response=response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar mensaje de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {str(e)}")

@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Obtiene información sobre una sesión de chat"""
    try:
        # Verificar que la sesión existe
        if not chat_service.session_exists(session_id):
            logger.warning(f"Sesión de chat no encontrada: {session_id}")
            raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
        
        # Obtener información de la sesión
        session_info = chat_service.get_session_info(session_id)
        
        return session_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener información de sesión de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Elimina una sesión de chat"""
    try:
        # Verificar que la sesión existe
        if not chat_service.session_exists(session_id):
            logger.warning(f"Sesión de chat no encontrada: {session_id}")
            raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
        
        # Eliminar la sesión
        success = chat_service.delete_session(session_id)
        
        if success:
            logger.info(f"Sesión de chat eliminada: {session_id}")
            return {"message": "Sesión de chat eliminada correctamente"}
        else:
            logger.warning(f"No se pudo eliminar la sesión de chat: {session_id}")
            raise HTTPException(status_code=500, detail="Error al eliminar la sesión de chat")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar sesión de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 