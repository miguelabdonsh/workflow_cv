# Analizador de Currículum

Sistema de análisis de currículum utilizando IA generativa (Gemini) para evaluar compatibilidad con descripciones de puestos.

## Arquitectura

El sistema utiliza una arquitectura modular basada en nodos para el procesamiento de currículum:

### Nodos de análisis

- **Nodo Extractor**: Responsable de extraer y estructurar el texto del CV
- **Nodo Clasificador**: Categoriza la información en secciones relevantes
- **Nodo Evaluador de Habilidades**: Analiza y puntúa habilidades técnicas y blandas

### Flujo de trabajo

El sistema implementa un flujo de trabajo donde los datos pasan secuencialmente entre nodos:

```
Extractor → Clasificador → Evaluador de Habilidades
```

### Intercambio de datos

- Utiliza modelos Pydantic para definir estructuras de datos entre nodos
- Cada nodo recibe datos estructurados y devuelve datos estructurados
- Implementa un sistema de caché para evitar reprocesamiento

## Características

- Análisis de compatibilidad con requisitos de puestos
- Evaluación detallada de habilidades técnicas y blandas
- Extracción de datos estructurados del CV
- Generación de resumen visual para toma de decisiones
- Caché para optimizar el rendimiento
- Procesamiento asíncrono para mejor experiencia de usuario

## Tecnologías

- **Backend**: FastAPI, Pydantic, PyMuPDF
- **Procesamiento ML**: Google Gemini AI
- **Frontend**: React, Tailwind CSS
- **Procesamiento asíncrono**: asyncio

## Instalación

1. Clonar el repositorio
2. Crear un archivo `.env` basado en `.env.example` con tu API key de Gemini
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Iniciar el backend

```bash
cd backend
uvicorn main:app --reload
```

### Iniciar el frontend

```bash
cd front
npm install
npm run dev
```

### Acceder a la aplicación

- Frontend: http://localhost:5173
- API Backend: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Estructura del proyecto

```
/
├── backend/                # Aplicación backend FastAPI
│   ├── app/
│   │   ├── models/         # Modelos de datos (Pydantic)
│   │   ├── routers/        # Endpoints de la API
│   │   └── services/       # Lógica de negocio
│   │       └── nodes/      # Nodos de procesamiento
│   └── main.py             # Punto de entrada del backend
├── front/                  # Aplicación frontend React
└── requirements.txt        # Dependencias de Python
```

## Escalabilidad futura

La arquitectura basada en nodos facilita:

- Añadir nuevos nodos de análisis sin modificar los existentes
- Procesamiento paralelo de nodos independientes
- Implementación de flujos de trabajo alternativos
- Integración con bases de datos para persistencia

## Licencia

MIT 