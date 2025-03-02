import React, { useState } from 'react';
import { AnalysisResult } from '../types';
import VisualSummary from './VisualSummary';
import DetailedAnalysis from './DetailedAnalysis';
import MultiCVChatPanel from './MultiCVChatPanel';
import { ChevronDown, ChevronUp, User, MessageCircle } from 'lucide-react';
import { getMatchScoreStyles } from '../utils/helpers';

interface ResultsListProps {
  results: AnalysisResult[];
  onReset: () => void;
  jobDescription: string;
}

const ResultsList: React.FC<ResultsListProps> = ({ results, onReset, jobDescription }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'resumen' | 'detalle'>('resumen');
  const [showGlobalChat, setShowGlobalChat] = useState(false);

  // Ordenar resultados por puntuación de compatibilidad (de mayor a menor)
  const sortedResults = [...results].sort((a, b) => b.match_score - a.match_score);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const renderMatchScore = (score: number) => {
    const { barColorClass, textColorClass, percentage } = getMatchScoreStyles(score);
    
    return (
      <div className="flex items-center w-24">
        <div className="w-full bg-gray-200 rounded-full h-2 mr-1">
          <div 
            className={`h-2 rounded-full ${barColorClass}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <span className={`text-xs font-medium ${textColorClass}`}>{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="border-t border-gray-200 bg-gray-50 p-6 md:p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">Resultados del Análisis</h2>
        <div className="flex space-x-4">
          <button
            onClick={() => setShowGlobalChat(true)}
            className="flex items-center gap-2 text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            <span>Chat sobre todos los candidatos</span>
          </button>
          <button
            onClick={onReset}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Analizar otros CVs
          </button>
        </div>
      </div>

      {/* Resultados */}
      <div className="space-y-4">
        {sortedResults.map((result, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm overflow-hidden">
            {/* Cabecera del candidato */}
            <div 
              className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
              onClick={() => toggleExpand(index)}
            >
              <div className="flex items-center">
                <div className="bg-blue-100 p-2 rounded-full mr-3">
                  <User className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-800">
                    {result.cv_data.nombre || `Candidato ${index + 1}`}
                  </h3>
                  {result.cv_data.correo && (
                    <p className="text-sm text-gray-500">{result.cv_data.correo}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {renderMatchScore(result.match_score)}
                {expandedIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>

            {/* Contenido expandible */}
            {expandedIndex === index && (
              <div className="border-t border-gray-100 p-4">
                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-6">
                  <button
                    className={`py-2 px-4 font-medium text-sm focus:outline-none ${
                      activeTab === 'resumen'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('resumen')}
                  >
                    Resumen Visual
                  </button>
                  <button
                    className={`py-2 px-4 font-medium text-sm focus:outline-none ${
                      activeTab === 'detalle'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('detalle')}
                  >
                    Detalle Completo
                  </button>
                </div>
                
                {/* Content based on active tab */}
                {activeTab === 'resumen' && (
                  <VisualSummary 
                    visualData={result.resumen_visual} 
                    nombre={result.cv_data.nombre} 
                  />
                )}
                
                {activeTab === 'detalle' && (
                  <DetailedAnalysis 
                    result={result} 
                    jobDescription={jobDescription}
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Chat global para todos los candidatos */}
      {showGlobalChat && (
        <MultiCVChatPanel 
          results={results} 
          onClose={() => setShowGlobalChat(false)} 
          jobDescription={jobDescription}
        />
      )}
    </div>
  );
};

export default ResultsList; 