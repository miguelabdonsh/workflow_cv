import fitz  # PyMuPDF
import os
import logging
from typing import Dict, Any

from pydantic import BaseModel

from .base_node import BaseNode
from ...models.node_schemas import CVDocument

# Configurar el logger
logger = logging.getLogger("cv_analyzer.nodes.extractor")

class ExtractorInput(BaseModel):
    """Modelo para la entrada del nodo extractor"""
    file_path: str
    mime_type: str = "application/pdf"

class ExtractorNode(BaseNode[ExtractorInput, CVDocument, Dict[str, Any]]):
    """Nodo responsable de extraer texto de archivos PDF (CVs)"""
    
    async def process(self, input_data: ExtractorInput, context: Dict[str, Any]) -> CVDocument:
        """Extrae texto del CV utilizando PyMuPDF"""
        file_path = input_data.file_path
        
        logger.info(f"Extracting text from file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.endswith('.pdf'):
            raise ValueError(f"Unsupported file format. Only PDF files are supported.")
        
        try:
            # Obtener información del archivo
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            # Extraer texto usando PyMuPDF
            text = self._extract_text_from_pdf(file_path)
            
            # Crear y devolver el documento CV
            cv_document = CVDocument(
                text=text,
                filename=filename,
                file_size=file_size,
                mime_type=input_data.mime_type
            )
            
            logger.info(f"Successfully extracted {len(text)} characters from {filename}")
            
            return cv_document
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Función auxiliar para extraer texto de un PDF usando PyMuPDF"""
        text = ""
        
        try:
            # Abrir el documento PDF
            doc = fitz.open(file_path)
            
            # Extraer texto de cada página
            total_pages = len(doc)
            logger.info(f"Processing {total_pages} pages from PDF")
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += page_text + "\n\n"
                
            # Cerrar el documento
            doc.close()
            
        except Exception as e:
            logger.error(f"Error in PDF text extraction: {str(e)}")
            raise
        
        return text 