import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Plus } from 'lucide-react';
import { CandidateFile } from '../types';

interface UploadFormProps {
  onAnalyze: (jobDescription: string, files: File[]) => void;
  isUploading: boolean;
  error: string;
}

const UploadForm: React.FC<UploadFormProps> = ({ onAnalyze, isUploading, error }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<CandidateFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    
    if (files && files.length > 0) {
      const newFiles: CandidateFile[] = [];
      
      // Convertir FileList a array para procesarlo
      Array.from(files).forEach(file => {
        // Verificar que sea un PDF
        if (file.type !== 'application/pdf') {
          return;
        }
        
        // Verificar tamaño máximo (5MB)
        if (file.size > 5 * 1024 * 1024) {
          return;
        }
        
        // Verificar que no exceda el límite de 5 archivos
        if (selectedFiles.length + newFiles.length >= 5) {
          return;
        }
        
        newFiles.push({
          file,
          name: file.name,
          size: file.size
        });
      });
      
      setSelectedFiles(prev => [...prev, ...newFiles].slice(0, 5));
    }
    
    // Limpiar el input para permitir seleccionar el mismo archivo nuevamente
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    
    if (files && files.length > 0) {
      const newFiles: CandidateFile[] = [];
      
      // Convertir FileList a array para procesarlo
      Array.from(files).forEach(file => {
        // Verificar que sea un PDF
        if (file.type !== 'application/pdf') {
          return;
        }
        
        // Verificar tamaño máximo (5MB)
        if (file.size > 5 * 1024 * 1024) {
          return;
        }
        
        // Verificar que no exceda el límite de 5 archivos
        if (selectedFiles.length + newFiles.length >= 5) {
          return;
        }
        
        newFiles.push({
          file,
          name: file.name,
          size: file.size
        });
      });
      
      setSelectedFiles(prev => [...prev, ...newFiles].slice(0, 5));
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleAnalyze = () => {
    if (selectedFiles.length === 0 || !jobDescription.trim()) return;
    onAnalyze(jobDescription, selectedFiles.map(f => f.file));
  };

  const isFormValid = jobDescription.trim().length > 0 && selectedFiles.length > 0;
  const canAddMoreFiles = selectedFiles.length < 5;

  return (
    <div className="p-6 md:p-8">
      <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-6">Analizador de Currículum</h1>
      
      {/* Job Description */}
      <div className="mb-6">
        <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-2">
          Descripción del puesto y requisitos
        </label>
        <textarea
          id="jobDescription"
          rows={5}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          placeholder="Ingresa la descripción del puesto y los requisitos necesarios para el candidato..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
      </div>
      
      {/* File Upload */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <p className="block text-sm font-medium text-gray-700">
            Currículums (PDF) - Máximo 5
          </p>
          <span className="text-sm text-gray-500">
            {selectedFiles.length}/5 archivos
          </span>
        </div>
        
        {/* Lista de archivos seleccionados */}
        {selectedFiles.length > 0 && (
          <div className="mb-3 space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-blue-50 p-3 rounded-md border border-blue-200">
                <div className="flex items-center">
                  <FileText className="h-5 w-5 text-blue-500 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => removeFile(index)}
                  className="text-gray-500 hover:text-red-500 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
        
        {/* Área de arrastrar y soltar */}
        {canAddMoreFiles && (
          <div
            className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors border-gray-300 hover:border-gray-400"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={triggerFileInput}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf"
              className="hidden"
              multiple
            />
            
            <div className="flex flex-col items-center">
              <Upload className="h-10 w-10 text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-700">
                Arrastra y suelta tus CVs aquí o haz clic para seleccionar
              </p>
              <p className="text-xs text-gray-500 mt-1">Solo archivos PDF (máx. 5MB cada uno)</p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}
      </div>
      
      {/* Submit Button */}
      <div className="flex justify-center">
        <button
          onClick={handleAnalyze}
          disabled={!isFormValid || isUploading}
          className={`px-6 py-3 rounded-md font-medium text-white transition-all ${
            isFormValid && !isUploading
              ? 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          {isUploading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analizando...
            </span>
          ) : (
            'Analizar CVs'
          )}
        </button>
      </div>
    </div>
  );
};

export default UploadForm; 