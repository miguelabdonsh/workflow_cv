import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultsList from './components/ResultsList';
import { AnalysisResult } from './types';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [jobDescription, setJobDescription] = useState('');

  const handleAnalyze = async (jobDesc: string, files: File[]) => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    setError('');
    setResults([]);
    setJobDescription(jobDesc);
    
    try {
      const analysisResults: AnalysisResult[] = [];
      
      // Procesar cada archivo secuencialmente
      for (const file of files) {
        const formData = new FormData();
        formData.append('job_description', jobDesc);
        formData.append('cv_file', file);
        
        const response = await fetch('http://localhost:8000/analyze-cv/', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Error al analizar el CV: ${file.name}`);
        }
        
        const data = await response.json();
        analysisResults.push(data as AnalysisResult);
      }
      
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