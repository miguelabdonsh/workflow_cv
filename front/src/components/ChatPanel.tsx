import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot } from 'lucide-react';
import { AnalysisResult } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  result: AnalysisResult;
  onClose: () => void;
  jobDescription?: string; // Nueva prop opcional para la descripción del trabajo
}

const ChatPanel: React.FC<ChatPanelProps> = ({ result, onClose, jobDescription = "" }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Inicializar la sesión de chat al montar el componente
  useEffect(() => {
    const initializeChat = async () => {
      try {
        console.log("Iniciando sesión de chat con datos completos del CV");
        const response = await fetch('http://localhost:8000/chat/sessions/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            cv_data: result.cv_data,
            job_description: jobDescription
          }),
        });

        if (!response.ok) {
          throw new Error('Error al crear la sesión de chat');
        }

        const data = await response.json();
        setSessionId(data.session_id);
        
        // Añadir mensaje inicial del asistente
        const welcomeMessage: ChatMessage = {
          role: 'assistant',
          content: `Hola, soy tu asistente para analizar el CV de ${result.cv_data.nombre || 'este candidato'}. ¿Qué te gustaría saber sobre este perfil?`,
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    initializeChat();

    // Limpiar la sesión al desmontar
    return () => {
      if (sessionId) {
        console.log("Cerrando sesión de chat:", sessionId);
        fetch(`http://localhost:8000/chat/sessions/${sessionId}`, {
          method: 'DELETE'
        }).catch(err => console.error('Error al eliminar la sesión:', err));
      }
    };
  }, [result.cv_data, jobDescription]);

  // Desplazar al último mensaje cuando se añaden nuevos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    // Añadir mensaje del usuario
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat/messages/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: inputMessage
        }),
      });

      if (!response.ok) {
        throw new Error('Error al procesar el mensaje');
      }

      const data = await response.json();
      
      // Añadir respuesta del asistente
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      
      // Mensaje de error
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[600px] max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 px-4 py-3 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-800">
            Chat sobre {result.cv_data.nombre || 'Candidato'}
          </h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-center mb-1">
                  {message.role === 'user' ? (
                    <>
                      <span className="text-xs opacity-75">Tú</span>
                      <User className="h-3 w-3 ml-1 opacity-75" />
                    </>
                  ) : (
                    <>
                      <Bot className="h-3 w-3 mr-1 opacity-75" />
                      <span className="text-xs opacity-75">Asistente</span>
                    </>
                  )}
                </div>
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Escribe un mensaje..."
              className="flex-1 border border-gray-300 rounded-l-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading || !sessionId}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim() || !sessionId}
              className={`bg-blue-500 text-white rounded-r-lg p-2 ${
                isLoading || !inputMessage.trim() || !sessionId
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-blue-600'
              }`}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel; 