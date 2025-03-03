import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultsList from './components/ResultsList';
import { AnalysisResult } from './types';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [jobDescription, setJobDescription] = useState('');

  // Función para esperar a que el análisis de CV se complete
  const waitForAnalysisResults = async (processId: string, maxAttempts = 30, delayMs = 1000): Promise<AnalysisResult> => {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await fetch(`http://localhost:8000/cv-results/${processId}`);
        
        if (!response.ok) {
          throw new Error(`Error al obtener resultados: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'completed') {
          return data.results;
        } else if (data.status === 'error') {
          throw new Error(data.error?.message || 'Error en el procesamiento del CV');
        }
        
        // Si aún está en proceso, esperar y reintentar
        await new Promise(resolve => setTimeout(resolve, delayMs));
        attempts++;
      } catch (err) {
        console.error('Error en consulta de resultados:', err);
        throw err;
      }
    }
    
    throw new Error('Tiempo de espera agotado para el procesamiento del CV');
  };

  // Función para iniciar el análisis de un solo CV
  const startCVAnalysis = async (file: File, jobDesc: string): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('job_description', jobDesc);
    formData.append('cv_file', file);
    
    // 1. Enviar el CV para iniciar el análisis
    const response = await fetch('http://localhost:8000/analyze-cv/', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error al analizar el CV: ${file.name}`);
    }
    
    // 2. Obtener el ID del proceso
    const initData = await response.json();
    const processId = initData.process_id;
    
    // 3. Esperar a que el proceso termine y obtener los resultados reales
    return await waitForAnalysisResults(processId);
  };

  // Función para limpiar resultados antiguos
  const clearOldResults = async (): Promise<void> => {
    try {
      const response = await fetch('http://localhost:8000/clear-results/', {
        method: 'POST'
      });
      
      if (!response.ok) {
        console.warn('No se pudieron limpiar los resultados antiguos');
      }
    } catch (err) {
      console.warn('Error al limpiar resultados antiguos:', err);
      // No lanzamos excepción para continuar con el análisis
    }
  };

  const handleAnalyze = async (jobDesc: string, files: File[]) => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError('');
    setResults([]);
    setJobDescription(jobDesc);
    
    try {
      // Limpiar resultados antiguos antes de iniciar
      await clearOldResults();
      
      // Iniciar todos los análisis en paralelo
      const analysisPromises = files.map(file => startCVAnalysis(file, jobDesc));
      
      // Esperar a que todos los análisis terminen
      const analysisResults = await Promise.all(analysisPromises);
      
      setResults(analysisResults);
    } catch (err) {
      console.error('Error:', err);
      setError(err instanceof Error ? err.message : 'Error al analizar los CVs');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setResults([]);
    setError('');
    setJobDescription('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Analizador de CVs</h1>
        
        {results.length > 0 ? (
          <ResultsList 
            results={results} 
            onReset={handleReset} 
            jobDescription={jobDescription}
          />
        ) : (
          <UploadForm 
            onAnalyze={handleAnalyze} 
            isUploading={isUploading} 
            error={error} 
          />
        )}
      </div>
    </div>
  );
}

export default App;