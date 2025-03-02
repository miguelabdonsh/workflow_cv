// Definir tipos para la estructura de datos del CV
export interface Education {
  institucion: string;
  titulo: string;
  campo: string;
  fecha_inicio: string;
  fecha_fin: string;
  descripcion?: string;
}

export interface Experience {
  empresa: string;
  puesto: string;
  fecha_inicio: string;
  fecha_fin: string;
  ubicacion: string;
  descripcion: string;
  tecnologias: string[];
}

export interface Language {
  idioma: string;
  nivel: string;
}

export interface Certification {
  nombre: string;
  emisor: string;
  fecha: string;
  expiracion?: string;
}

export interface Project {
  nombre: string;
  descripcion: string;
  tecnologias: string[];
  url?: string;
}

export interface Reference {
  nombre: string;
  relacion: string;
  empresa: string;
  contacto?: string;
}

export interface SkillHighlight {
  habilidad: string;
  nivel: string;
  relevancia: string;
}

export interface VisualSummary {
  perfil_candidato: string;
  compatibilidad_general: string;
  nivel_compatibilidad: number;
  campo_candidato?: string;
  campo_solicitado?: string;
  match_campo?: boolean;
  puntos_clave: string[];
  habilidades_destacadas: SkillHighlight[];
  experiencia_relevante: string;
  recomendacion_final: string;
}

export interface CVData {
  nombre?: string;
  correo?: string;
  telefono?: string;
  ubicacion?: string;
  linkedin?: string;
  resumen?: string;
  educacion: Education[];
  experiencia: Experience[];
  habilidades_tecnicas: string[];
  habilidades_blandas: string[];
  idiomas: Language[];
  certificaciones: Certification[];
  proyectos: Project[];
  logros: string[];
  intereses: string[];
  referencias: Reference[];
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

export interface CandidateFile {
  file: File;
  name: string;
  size: number;
}

export interface MultipleAnalysisResult {
  results: AnalysisResult[];
  jobDescription: string;
} 