export interface CVData {
  nombre?: string;
  correo?: string;
  telefono?: string;
  ubicacion?: string;
  linkedin?: string;
  resumen?: string;
  educacion?: Array<any>;
  experiencia?: Array<any>;
  habilidades_tecnicas?: string[];
  habilidades_blandas?: string[];
  idiomas?: Array<{ idioma: string; nivel: string }>;
  certificaciones?: Array<any>;
  proyectos?: Array<any>;
  logros?: string[];
  intereses?: string[];
  referencias?: Array<any>;
}

export interface VisualSummary {
  perfil_candidato: string;
  compatibilidad_general: string;
  nivel_compatibilidad: number;
  campo_candidato?: string;
  campo_solicitado?: string;
  match_campo?: boolean;
  puntos_clave: string[];
  habilidades_destacadas: Array<{
    habilidad: string;
    nivel: string;
    relevancia: string;
  }>;
  experiencia_relevante: string;
  recomendacion_final: string;
}

export interface AnalysisResult {
  cv_data: CVData;
  match_score: number;
  fortalezas: string[];
  areas_mejora: string[];
  recomendaciones: string[];
  justificacion_puntuacion?: string;
  campo_principal_candidato?: string;
  campo_solicitado?: string;
  match_campo?: boolean;
  resumen_visual: VisualSummary;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  cv_name?: string;
  message_count: number;
  recent_messages: ChatMessage[];
} 