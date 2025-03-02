import React, { useState } from 'react';
import ChatPanel from './ChatPanel';

const CVAnalyzer: React.FC = () => {
  const [showChat, setShowChat] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [jobDescription, setJobDescription] = useState<string | null>(null);

  const handleAnalysisResult = (result: string) => {
    setAnalysisResult(result);
    setShowChat(true);
  };

  return (
    <div>
      {showChat && analysisResult && (
        <ChatPanel 
          result={analysisResult} 
          onClose={() => setShowChat(false)} 
          jobDescription={jobDescription}
        />
      )}
    </div>
  );
};

export default CVAnalyzer; 