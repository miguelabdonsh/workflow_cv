import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultsList from './components/ResultsList';
import { AnalysisResult } from './types';
import { API_URL } from './config';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [jobDescription, setJobDescription] = useState('');

  // Función de utilidad para esperar un tiempo
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  // Función para enviar un CV con reintentos
  const sendCVWithRetry = async (file: File, jobDesc: string, index: number, maxRetries = 2): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('job_description', jobDesc);
    formData.append('cv_file', file);
    
    console.log(`Enviando CV ${index + 1}: ${file.name} para análisis paralelo`);
    
    let lastError;
    // Intentar la solicitud con reintentos
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Si no es el primer intento, esperar antes de reintentar
        if (attempt > 0) {
          console.log(`Reintentando CV ${index + 1} (intento ${attempt})...`);
          await delay(500 * attempt); // Esperar más tiempo en cada reintento
        }
        
        // Usar un timeout para evitar que la solicitud se quede colgada
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 segundos timeout
        
        const response = await fetch(`${API_URL}/analyze-cv/`, {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Error al analizar el CV: ${file.name}`);
        }
        
        const data = await response.json();
        console.log(`CV procesado ${index + 1}: ${file.name} - Éxito!`);
        return data as AnalysisResult;
      } catch (err) {
        lastError = err;
        console.error(`Error en CV ${index + 1} (intento ${attempt}):`, err);
        // Si es el último intento, propagar el error
        if (attempt === maxRetries) throw err;
      }
    }
    
    throw lastError;
  };

  const handleAnalyze = async (jobDesc: string, files: File[]) => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError('');
    setResults([]);
    setJobDescription(jobDesc);
    
    try {
      console.log(`Usando API en: ${API_URL}`);
      
      // Crear un array de promesas (una por cada CV)
      const analysisPromises = files.map((file, index) => 
        sendCVWithRetry(file, jobDesc, index)
      );
      
      // Esperar a que todas las promesas se resuelvan (en paralelo)
      console.log(`Procesando ${files.length} CVs en paralelo...`);
      const startTime = new Date().getTime();
      
      const analysisResults = await Promise.all(analysisPromises);
      
      const endTime = new Date().getTime();
      const totalTime = (endTime - startTime) / 1000;
      console.log(`Todos los CVs procesados en ${totalTime} segundos`);
      console.log(`Tiempo promedio por CV: ${totalTime / files.length} segundos`);
      
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