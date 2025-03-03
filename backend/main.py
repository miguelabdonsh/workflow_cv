from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.routers import cv_router, chat_router, batch_router

# Configurar el sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cv_analyzer")

app = FastAPI(title="CV Analyzer API")

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # URLs del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(cv_router.router, prefix="")
app.include_router(chat_router.router, prefix="")
app.include_router(batch_router.router, prefix="")  # Nuevo router para procesamiento por lotes

@app.on_event("startup")
async def startup_event():
    logger.info("=== Iniciando servidor de CV Analyzer ===")
    logger.info(f"Directorio de trabajo: {os.getcwd()}")
    
    # Crear el directorio para los resultados si no existe
    results_dir = os.path.join(os.getcwd(), "resultados")
    os.makedirs(results_dir, exist_ok=True)
    logger.info(f"Directorio de resultados: {results_dir}")
    
    logger.info("API disponible en http://localhost:8000")
    logger.info("Documentación disponible en http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== Deteniendo servidor de CV Analyzer ===")

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor con Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 