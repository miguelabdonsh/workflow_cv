import React, { useState } from 'react';
import { Star, Award, Book, Briefcase, Code, Globe, Heart, CheckCircle, AlertCircle, MessageSquare, Check } from 'lucide-react';
import { AnalysisResult } from '../types';
import { getMatchScoreStyles } from '../utils/helpers';
import ChatPanel from './ChatPanel';

interface DetailedAnalysisProps {
  result: AnalysisResult;
  jobDescription: string;
}

const DetailedAnalysis: React.FC<DetailedAnalysisProps> = ({ result, jobDescription }) => {
  const [showChat, setShowChat] = useState(false);

  // Función para renderizar la puntuación de compatibilidad
  const renderMatchScore = (score: number) => {
    const { barColorClass, textColorClass, percentage } = getMatchScoreStyles(score);
    
    return (
      <div className="mt-1">
        <div className="flex justify-between mb-1">
          <span className="text-sm text-gray-700">Compatibilidad:</span>
          <span className={`text-sm font-medium ${textColorClass}`}>{percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className={`${barColorClass} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Botón para iniciar chat */}
      <div className="flex justify-end">
        <button
          onClick={() => setShowChat(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <MessageSquare className="h-5 w-5" />
          <span>Preguntar sobre este candidato</span>
        </button>
      </div>

      {/* Candidate Info */}
      {result.cv_data.nombre && (
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">{result.cv_data.nombre}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            {result.cv_data.correo && <p className="text-gray-600"><span className="font-medium">Email:</span> {result.cv_data.correo}</p>}
            {result.cv_data.telefono && <p className="text-gray-600"><span className="font-medium">Teléfono:</span> {result.cv_data.telefono}</p>}
            {result.cv_data.ubicacion && <p className="text-gray-600"><span className="font-medium">Ubicación:</span> {result.cv_data.ubicacion}</p>}
            {result.cv_data.linkedin && (
              <p className="text-gray-600">
                <span className="font-medium">LinkedIn:</span>
                <a 
                  href={result.cv_data.linkedin.startsWith('http') ? result.cv_data.linkedin : `https://${result.cv_data.linkedin}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {result.cv_data.linkedin}
                </a>
              </p>
            )}
          </div>
          {result.cv_data.resumen && (
            <div className="mt-3 text-sm text-gray-600">
              <p className="font-medium">Resumen:</p>
              <p>{result.cv_data.resumen}</p>
            </div>
          )}
        </div>
      )}
      
      {/* Match Score */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
        <div className="flex items-center mb-2">
          <Star className="h-5 w-5 text-yellow-500 mr-2" />
          <h3 className="text-lg font-semibold text-gray-800">Compatibilidad con el puesto</h3>
        </div>
        {renderMatchScore(result.match_score)}
        
        {/* Nueva sección: Explicación de compatibilidad */}
        {result.justificacion_puntuacion && (
          <div className="mt-3 text-sm">
            <h4 className="font-medium text-gray-700 mb-1">Justificación de puntuación:</h4>
            <p className="text-gray-600">{result.justificacion_puntuacion}</p>
          </div>
        )}
        
        {/* Información de campos */}
        {result.campo_principal_candidato && (
          <div className="mt-3 p-3 bg-gray-50 rounded">
            <div className="flex justify-between text-sm mb-2">
              <div>
                <span className="text-gray-500">Campo del candidato:</span>
                <p className="font-medium">{result.campo_principal_candidato}</p>
              </div>
              <div>
                <span className="text-gray-500">Campo del puesto:</span>
                <p className="font-medium">{result.campo_solicitado}</p>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <div className={`rounded-full p-1 mr-2 ${result.match_campo ? 'bg-green-100' : 'bg-yellow-100'}`}>
                {result.match_campo ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                )}
              </div>
              <span className={result.match_campo ? 'text-green-700' : 'text-yellow-700'}>
                {result.match_campo ? 'Campos coincidentes' : 'Campos diferentes'}
              </span>
            </div>
          </div>
        )}
      </div>
      
      {/* Analysis Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Strengths */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex items-center mb-2">
            <Award className="h-5 w-5 text-green-500 mr-2" />
            <h3 className="font-semibold text-gray-800">Fortalezas</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            {result.fortalezas.map((strength, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-500 mr-1">✓</span> {strength}
              </li>
            ))}
          </ul>
        </div>
        
        {/* Areas to Improve */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex items-center mb-2">
            <Book className="h-5 w-5 text-yellow-500 mr-2" />
            <h3 className="font-semibold text-gray-800">Áreas de mejora</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            {result.areas_mejora.map((area, index) => (
              <li key={index} className="flex items-start">
                <span className="text-yellow-500 mr-1">•</span> {area}
              </li>
            ))}
          </ul>
        </div>
        
        {/* Recommendations */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <div className="flex items-center mb-2">
            <Briefcase className="h-5 w-5 text-blue-500 mr-2" />
            <h3 className="font-semibold text-gray-800">Recomendaciones</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            {result.recomendaciones.map((recommendation, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-500 mr-1">→</span> {recommendation}
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* CV Details Accordion */}
      <div className="space-y-4">
        {/* Experience */}
        {result.cv_data.experiencia.length > 0 && (
          <details className="bg-white rounded-lg shadow-sm">
            <summary className="p-4 cursor-pointer font-semibold text-gray-800 flex items-center">
              <Briefcase className="h-5 w-5 text-gray-500 mr-2" />
              Experiencia Laboral
            </summary>
            <div className="p-4 pt-0 border-t border-gray-100">
              {result.cv_data.experiencia.map((exp, index) => (
                <div key={index} className="mb-4 last:mb-0">
                  <div className="flex justify-between items-start">
                    <h4 className="font-medium text-gray-800">{exp.puesto}</h4>
                    <span className="text-sm text-gray-500">{exp.fecha_inicio} - {exp.fecha_fin}</span>
                  </div>
                  <p className="text-sm text-gray-600">{exp.empresa}, {exp.ubicacion}</p>
                  <p className="text-sm text-gray-600 mt-1">{exp.descripcion}</p>
                  {exp.tecnologias.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {exp.tecnologias.map((tech, techIndex) => (
                        <span key={techIndex} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </details>
        )}
        
        {/* Education */}
        {result.cv_data.educacion.length > 0 && (
          <details className="bg-white rounded-lg shadow-sm">
            <summary className="p-4 cursor-pointer font-semibold text-gray-800 flex items-center">
              <Book className="h-5 w-5 text-gray-500 mr-2" />
              Educación
            </summary>
            <div className="p-4 pt-0 border-t border-gray-100">
              {result.cv_data.educacion.map((edu, index) => (
                <div key={index} className="mb-4 last:mb-0">
                  <div className="flex justify-between items-start">
                    <h4 className="font-medium text-gray-800">{edu.titulo}</h4>
                    <span className="text-sm text-gray-500">{edu.fecha_inicio} - {edu.fecha_fin}</span>
                  </div>
                  <p className="text-sm text-gray-600">{edu.institucion}</p>
                  <p className="text-sm text-gray-600">{edu.campo}</p>
                  {edu.descripcion && <p className="text-sm text-gray-600 mt-1">{edu.descripcion}</p>}
                </div>
              ))}
            </div>
          </details>
        )}
        
        {/* Skills */}
        {(result.cv_data.habilidades_tecnicas.length > 0 || result.cv_data.habilidades_blandas.length > 0) && (
          <details className="bg-white rounded-lg shadow-sm">
            <summary className="p-4 cursor-pointer font-semibold text-gray-800 flex items-center">
              <Code className="h-5 w-5 text-gray-500 mr-2" />
              Habilidades
            </summary>
            <div className="p-4 pt-0 border-t border-gray-100">
              {result.cv_data.habilidades_tecnicas.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-800 mb-2">Habilidades Técnicas</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.cv_data.habilidades_tecnicas.map((skill, skillIndex) => (
                      <span key={skillIndex} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {result.cv_data.habilidades_blandas.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Habilidades Blandas</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.cv_data.habilidades_blandas.map((skill, skillIndex) => (
                      <span key={skillIndex} className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </details>
        )}
        
        {/* Languages */}
        {result.cv_data.idiomas.length > 0 && (
          <details className="bg-white rounded-lg shadow-sm">
            <summary className="p-4 cursor-pointer font-semibold text-gray-800 flex items-center">
              <Globe className="h-5 w-5 text-gray-500 mr-2" />
              Idiomas
            </summary>
            <div className="p-4 pt-0 border-t border-gray-100">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {result.cv_data.idiomas.map((lang, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-800">{lang.idioma}</span>
                    <span className="text-sm text-gray-600">{lang.nivel}</span>
                  </div>
                ))}
              </div>
            </div>
          </details>
        )}
        
        {/* Other Sections (Projects, Certifications, etc.) */}
        {(result.cv_data.proyectos.length > 0 || 
          result.cv_data.certificaciones.length > 0 || 
          result.cv_data.logros.length > 0 || 
          result.cv_data.intereses.length > 0) && (
          <details className="bg-white rounded-lg shadow-sm">
            <summary className="p-4 cursor-pointer font-semibold text-gray-800 flex items-center">
              <Heart className="h-5 w-5 text-gray-500 mr-2" />
              Información Adicional
            </summary>
            <div className="p-4 pt-0 border-t border-gray-100">
              {/* Projects */}
              {result.cv_data.proyectos.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-800 mb-2">Proyectos</h4>
                  {result.cv_data.proyectos.map((project, index) => (
                    <div key={index} className="mb-3 last:mb-0">
                      <div className="flex justify-between items-start">
                        <h5 className="font-medium text-gray-700">{project.nombre}</h5>
                        {project.url && (
                          <a href={project.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">
                            Ver proyecto
                          </a>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{project.descripcion}</p>
                      {project.tecnologias.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {project.tecnologias.map((tech, techIndex) => (
                            <span key={techIndex} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {/* Certifications */}
              {result.cv_data.certificaciones.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-800 mb-2">Certificaciones</h4>
                  {result.cv_data.certificaciones.map((cert, index) => (
                    <div key={index} className="mb-2 last:mb-0">
                      <div className="flex justify-between items-start">
                        <h5 className="font-medium text-gray-700">{cert.nombre}</h5>
                        <span className="text-xs text-gray-500">{cert.fecha}</span>
                      </div>
                      <p className="text-sm text-gray-600">{cert.emisor}</p>
                      {cert.expiracion && <p className="text-xs text-gray-500">Expira: {cert.expiracion}</p>}
                    </div>
                  ))}
                </div>
              )}
              
              {/* Achievements */}
              {result.cv_data.logros.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-800 mb-2">Logros</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600">
                    {result.cv_data.logros.map((achievement, index) => (
                      <li key={index}>{achievement}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Interests */}
              {result.cv_data.intereses.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Intereses</h4>
                  <div className="flex flex-wrap gap-1">
                    {result.cv_data.intereses.map((interest, index) => (
                      <span key={index} className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </details>
        )}
      </div>

      {/* Chat Panel */}
      {showChat && <ChatPanel result={result} onClose={() => setShowChat(false)} jobDescription={jobDescription} />}
    </div>
  );
};

export default DetailedAnalysis; 