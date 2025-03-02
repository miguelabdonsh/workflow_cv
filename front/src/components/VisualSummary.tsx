import React from 'react';
import { BarChart, FileBarChart, ThumbsUp, ThumbsDown, User, Star, Check, Code, Briefcase } from 'lucide-react';
import { VisualSummary as VisualSummaryType } from '../types';
import { getMatchScoreStyles, getRelevanceColor, getLevelColor } from '../utils/helpers';

interface VisualSummaryProps {
  visualData: VisualSummaryType;
  nombre?: string;
}

const VisualSummary: React.FC<VisualSummaryProps> = ({ visualData, nombre }) => {
  // Función para renderizar la puntuación de compatibilidad
  const renderMatchScore = (score: number) => {
    const { barColorClass, textColorClass, percentage } = getMatchScoreStyles(score);
    
    return (
      <div className="flex items-center">
        <div className="w-full bg-gray-200 rounded-full h-4 mr-2">
          <div 
            className={`h-4 rounded-full ${barColorClass}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <span className={`font-bold ${textColorClass}`}>{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Perfil y Compatibilidad */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex items-start space-x-4">
          <div className="bg-blue-100 p-3 rounded-full">
            <User className="h-8 w-8 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Perfil del Candidato</h3>
            <p className="text-gray-700">{visualData.perfil_candidato}</p>
            
            <div className="mt-6 flex items-center">
              <div className={`rounded-full p-1 ${visualData.nivel_compatibilidad >= 0.6 ? 'bg-green-100' : 'bg-yellow-100'}`}>
                {visualData.nivel_compatibilidad >= 0.6 ? (
                  <ThumbsUp className="h-5 w-5 text-green-600" />
                ) : (
                  <ThumbsDown className="h-5 w-5 text-yellow-600" />
                )}
              </div>
              <p className="ml-2 text-gray-700 font-medium">{visualData.compatibilidad_general}</p>
            </div>

            {/* Nueva sección: Información de campo */}
            {visualData.campo_candidato && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <Briefcase className="h-4 w-4 text-gray-600 mr-2" />
                  <span className="text-sm font-semibold">Coincidencia de Campo:</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-gray-600">Campo del Candidato:</p>
                    <p className="font-medium">{visualData.campo_candidato}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Campo del Puesto:</p>
                    <p className="font-medium">{visualData.campo_solicitado}</p>
                  </div>
                </div>
                <div className="mt-2 flex items-center">
                  {visualData.match_campo ? (
                    <>
                      <div className="bg-green-100 p-1 rounded-full">
                        <Check className="h-4 w-4 text-green-600" />
                      </div>
                      <p className="ml-2 text-green-700 text-sm font-medium">
                        Campos coincidentes
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="bg-yellow-100 p-1 rounded-full">
                        <ThumbsDown className="h-4 w-4 text-yellow-600" />
                      </div>
                      <p className="ml-2 text-yellow-700 text-sm font-medium">
                        Campos diferentes
                      </p>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Match Score */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center mb-4">
          <Star className="h-6 w-6 text-yellow-500 mr-2" />
          <h3 className="text-lg font-bold text-gray-800">Compatibilidad con el Puesto</h3>
        </div>
        {renderMatchScore(visualData.nivel_compatibilidad * 100)}
      </div>
      
      {/* Puntos Clave */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex items-center mb-4">
          <Star className="h-6 w-6 text-amber-500 mr-2" />
          <h3 className="text-lg font-bold text-gray-800">Puntos Clave</h3>
        </div>
        <ul className="space-y-2">
          {visualData.puntos_clave.map((punto, index) => (
            <li key={index} className="flex items-start">
              <div className="bg-blue-100 p-1 rounded-full mt-0.5 mr-2">
                <Check className="h-4 w-4 text-blue-600" />
              </div>
              <span className="text-gray-700">{punto}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Habilidades Destacadas */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex items-center mb-4">
          <Code className="h-6 w-6 text-indigo-600 mr-2" />
          <h3 className="text-lg font-bold text-gray-800">Habilidades Destacadas</h3>
        </div>
        <div className="space-y-3">
          {visualData.habilidades_destacadas.map((skill, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center">
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium mr-2 ${getRelevanceColor(skill.relevancia)}`}>
                  {skill.relevancia}
                </span>
                <span className="text-gray-800 font-medium">{skill.habilidad}</span>
              </div>
              <span className={`text-sm font-medium ${getLevelColor(skill.nivel)}`}>
                {skill.nivel}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Experiencia Relevante */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex items-center mb-4">
          <Briefcase className="h-6 w-6 text-gray-700 mr-2" />
          <h3 className="text-lg font-bold text-gray-800">Experiencia Relevante</h3>
        </div>
        <p className="text-gray-700">{visualData.experiencia_relevante}</p>
      </div>
      
      {/* Recomendación Final */}
      <div className={`p-6 rounded-lg shadow-sm ${visualData.recomendacion_final.toLowerCase().includes('contratar') || visualData.recomendacion_final.toLowerCase().includes('recomend') ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
        <div className="flex items-center mb-2">
          <FileBarChart className="h-6 w-6 text-gray-700 mr-2" />
          <h3 className="text-lg font-bold text-gray-800">Recomendación Final</h3>
        </div>
        <p className="text-gray-700 font-medium">{visualData.recomendacion_final}</p>
      </div>
    </div>
  );
};

export default VisualSummary; 