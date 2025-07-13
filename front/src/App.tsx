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
  const sendCVWithRetry = async (file: File, jobDesc: string, index: number, maxRetries = 1): Promise<AnalysisResult> => {
    console.log(`Enviando CV ${index + 1}: ${file.name} para análisis paralelo`);
    
    // Crear FormData fuera del ciclo de reintentos
    const formData = new FormData();
    formData.append('cv_file', file);
    formData.append('job_description', jobDesc);
    
    // Depuración adicional
    console.log('Contenido del FormData:');
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + (pair[1] instanceof File ? 
        `File: ${(pair[1] as File).name}, ${(pair[1] as File).size} bytes, type: ${(pair[1] as File).type}` : 
        pair[1]));
    }
    
    // Timeout más corto para evitar bloqueos
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    
    try {
      const response = await fetch(`${API_URL}/analyze-cv/`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Error ${response.status}: ${errorText}`);
        throw new Error(`Error HTTP: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error procesando CV ${file.name}:`, error);
      throw error;
    }
  };

  const handleAnalyze = async (jobDesc: string, files: File[]) => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError('');
    setResults([]);
    setJobDescription(jobDesc);
    
    const startTime = performance.now();
    console.log(`Procesando ${files.length} CVs en paralelo...`);
    
    // Crear todas las promesas a la vez, sin bloqueos entre ellas
    const batchSize = 10; // Procesar en lotes de 10 para máximo paralelismo
    const batches = [];
    
    for (let i = 0; i < files.length; i += batchSize) {
      const batch = files.slice(i, i + batchSize).map((file, idx) => 
        sendCVWithRetry(file, jobDesc, i + idx)
      );
      batches.push(batch);
    }
    
    try {
      // Procesar primero el lote inicial para maximizar paralelismo
      const initialResults = await Promise.all(batches[0]);
      setResults(prevResults => [...prevResults, ...initialResults]);
      
      // Procesar lotes adicionales si existen
      for (let i = 1; i < batches.length; i++) {
        const batchResults = await Promise.all(batches[i]);
        setResults(prevResults => [...prevResults, ...batchResults]);
      }
      
      const endTime = performance.now();
      console.log(`Todos los CVs procesados en ${((endTime - startTime) / 1000).toFixed(2)} segundos`);
    } catch (error) {
      console.error("Error procesando CVs:", error);
      setError("Error procesando algunos CVs. Intente nuevamente.");
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