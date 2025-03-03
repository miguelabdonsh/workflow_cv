import fitz  # PyMuPDF
import os
import logging
from typing import Dict, Any
from datetime import datetime

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
        start_time = datetime.now()
        
        logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Extracting text from file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.endswith('.pdf'):
            logger.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unsupported file format: {file_path}")
            raise ValueError(f"Unsupported file format. Only PDF files are supported.")
        
        try:
            # Obtener información del archivo
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Procesando archivo: {filename} ({file_size/1024:.2f} KB)")
            
            # Extraer texto usando PyMuPDF
            extraction_start_time = datetime.now()
            logger.info(f"[{extraction_start_time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando extracción de texto del PDF")
            text = self._extract_text_from_pdf(file_path)
            extraction_end_time = datetime.now()
            extraction_duration = (extraction_end_time - extraction_start_time).total_seconds()
            logger.info(f"[{extraction_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Extracción de texto completada en {extraction_duration:.2f} segundos")
            
            # Crear y devolver el documento CV
            cv_document = CVDocument(
                text=text,
                filename=filename,
                file_size=file_size,
                mime_type=input_data.mime_type
            )
            
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            logger.info(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully extracted {len(text)} characters from {filename} in {total_duration:.2f} seconds")
            
            return cv_document
            
        except Exception as e:
            error_time = datetime.now()
            logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Función auxiliar para extraer texto de un PDF usando PyMuPDF"""
        text = ""
        
        try:
            # Abrir el documento PDF
            start_time = datetime.now()
            doc = fitz.open(file_path)
            
            # Extraer texto de cada página
            total_pages = len(doc)
            logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Processing {total_pages} pages from PDF")
            
            for page_num in range(total_pages):
                page_start_time = datetime.now()
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += page_text + "\n\n"
                page_end_time = datetime.now()
                page_duration = (page_end_time - page_start_time).total_seconds()
                logger.info(f"[{page_end_time.strftime('%Y-%m-%d %H:%M:%S')}] Página {page_num+1}/{total_pages} procesada en {page_duration:.2f} segundos ({len(page_text)} caracteres)")
                
            # Cerrar el documento
            doc.close()
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            logger.info(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] PDF procesado completamente en {total_duration:.2f} segundos")
            
        except Exception as e:
            error_time = datetime.now()
            logger.error(f"[{error_time.strftime('%Y-%m-%d %H:%M:%S')}] Error in PDF text extraction: {str(e)}")
            raise
        
        return text 