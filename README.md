# Analizador de Currículum

Sistema de análisis de currículum utilizando IA generativa (Gemini) para evaluar compatibilidad con descripciones de puestos.

## Arquitectura Técnica

El sistema implementa una arquitectura modular basada en nodos para el procesamiento de currículum, permitiendo un flujo de datos estructurado y extensible.

### Core: Nodos de Procesamiento

La unidad fundamental del sistema es el `BaseNode`, una clase abstracta genérica que define el comportamiento base para todos los nodos:

```python
class BaseNode(Generic[InputT, OutputT, ContextT], ABC):
    async def process(self, input_data: InputT, context: ContextT) -> OutputT:
        pass
        
    async def execute(self, input_data: InputT, context: ContextT = None) -> tuple[OutputT, NodeMetadata]:
        # Implementación con medición, caché y manejo de errores
```

### Nodos Principales de Análisis

- **ExtractorNode**: Extrae texto y metadatos de archivos PDF
  - Input: `ExtractorInput(file_path, mime_type)`
  - Output: `CVDocument(text, filename, file_size, extraction_date, mime_type)`

- **ClassifierNode**: Categoriza el texto en secciones estructuradas
  - Input: `CVDocument`
  - Output: `ClassifiedCV(nombre, correo, telefono, ubicacion, educacion_texto, experiencia_texto, etc.)`

- **SkillsEvaluatorNode**: Analiza y evalúa habilidades con respecto a requisitos
  - Input: `SkillsEvaluatorInput(classified_cv, job_description)`
  - Output: `SkillsEvaluation(habilidades_tecnicas, habilidades_blandas, puntuacion_general, etc.)`

- **ChatNode**: Permite interacción conversacional con los resultados del análisis
  - Input: `ChatInput(session_id, message, cv_data, job_description, etc.)`
  - Output: `ChatOutput(response, session_id)`

### Gestor de Flujo de Trabajo

La clase `WorkflowManager` orquesta la ejecución de los nodos:

```python
workflow = WorkflowManager("CVAnalysisWorkflow")
workflow.add_node(extractor_node)
workflow.add_node(classifier_node)
workflow.add_node(skills_evaluator_node)

workflow.connect("extractor_node", "classifier_node")
workflow.connect("classifier_node", "skills_evaluator_node")

result = await workflow.execute("extractor_node", initial_input, context)
```

Características del gestor:
- Ejecución secuencial o paralela de nodos
- Seguimiento de metadatos de ejecución
- Sistema de estado para monitorear el progreso
- Manejo de caché para resultados intermedios

### Modelos de Datos (Pydantic)

El proyecto utiliza modelos Pydantic extensamente para asegurar una transferencia de datos tipada y validada:

#### Modelos Base de Análisis de CV
```python
class CVDocument(BaseModel):
    """Texto extraído y metadatos del CV"""
    text: str
    filename: str
    file_size: int
    extraction_date: datetime
    mime_type: str

class ClassifiedCV(BaseModel):
    """Información categorizada por secciones"""
    nombre: Optional[str]
    correo: Optional[str]
    # Más campos estructurados...

class SkillsEvaluation(BaseModel):
    """Evaluación de habilidades"""
    habilidades_tecnicas: List[HabilidadEvaluada]
    habilidades_blandas: List[HabilidadEvaluada]
    puntuacion_general: float
    # Más campos de evaluación...
```

#### Modelos de Chat
```python
class ChatSession(BaseModel):
    """Sesión de chat con historial y contexto"""
    session_id: str
    messages: List[ChatMessage]
    cv_data: Optional[Dict[str, Any]]
    job_description: Optional[str]
    # Campos adicionales para contexto...
```

## API y Endpoints

El sistema expone dos grupos principales de endpoints:

### Análisis de CV (cv_router.py)
- POST `/analyze-cv/` - Analiza un CV contra una descripción de puesto
- GET `/workflow-status/` - Obtiene el estado del flujo de trabajo
- POST `/clear-caches/` - Limpia las cachés de los nodos

### Interacción por Chat (chat_router.py)
- POST `/chat/sessions/` - Crea una nueva sesión de chat para un CV
- POST `/chat/multi-sessions/` - Crea sesión con múltiples CVs comparados
- POST `/chat/messages/` - Envía mensajes a una sesión de chat
- GET `/chat/sessions/{session_id}` - Obtiene información de sesión
- DELETE `/chat/sessions/{session_id}` - Elimina una sesión

## Interfaz de Usuario React

La interfaz está construida con React y TypeScript, con componentes modulares:

### Componentes Principales
- **UploadForm** - Carga de CV y descripción de trabajo
- **ResultsList** - Lista ordenada de resultados de análisis
- **DetailedAnalysis** - Visualización detallada del análisis
- **VisualSummary** - Resumen visual con gráficos de compatibilidad
- **ChatPanel** - Interfaz conversacional para un CV
- **MultiCVChatPanel** - Comparación conversacional de múltiples CVs

## Características Técnicas Adicionales

- **Caché integrada** en los nodos para optimizar rendimiento
- **Medición de tiempos de ejecución** para análisis de rendimiento
- **Sistema de metadatos** para seguimiento de ejecución
- **Procesamiento asíncrono** con asyncio
- **Integración con Gemini AI** para análisis semántico avanzado
- **Sesiones de chat persistentes** para consulta interactiva

## Tecnologías

- **Backend**: FastAPI, Pydantic, PyMuPDF, AsyncIO
- **Procesamiento ML**: Google Gemini 2.0 Flash (API)
- **Frontend**: React, TypeScript, Tailwind CSS
- **Herramientas de desarrollo**: Vite, ESLint

## Instalación

1. Clonar el repositorio
2. Crear un archivo `.env` basado en `.env.example` con tu API key de Gemini
3. Instalar dependencias de backend:

```bash
cd backend
pip install -r requirements.txt
```

4. Instalar dependencias de frontend:

```bash
cd front
npm install
```

## Desarrollo y Ejecución

### Iniciar el backend

```bash
cd backend
uvicorn main:app --reload
```

### Iniciar el frontend

```bash
cd front
npm run dev
```

### Acceder a la aplicación

- Frontend: http://localhost:5173
- API Backend: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Arquitectura de Archivos

```
/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── node_schemas.py    # Modelos de datos para nodos
│   │   │   └── schemas.py         # Modelos de API y respuestas
│   │   ├── routers/
│   │   │   ├── cv_router.py       # Endpoints de análisis de CV
│   │   │   └── chat_router.py     # Endpoints de interacción por chat
│   │   └── services/
│   │       ├── cv_analyzer.py     # Servicio de análisis
│   │       ├── chat_service.py    # Servicio de conversación
│   │       └── nodes/             # Implementación de nodos
│   │           ├── base_node.py   # Clase base abstracta
│   │           ├── extractor_node.py
│   │           ├── classifier_node.py
│   │           ├── skills_evaluator_node.py
│   │           ├── chat_node.py
│   │           └── workflow.py    # Gestor de flujo de trabajo
│   └── main.py                    # Punto de entrada
├── front/
│   ├── src/
│   │   ├── components/            # Componentes React
│   │   │   ├── UploadForm.tsx     # Carga de archivos
│   │   │   ├── ResultsList.tsx    # Lista de resultados
│   │   │   ├── DetailedAnalysis.tsx  # Análisis detallado
│   │   │   ├── VisualSummary.tsx  # Resumen visual
│   │   │   ├── ChatPanel.tsx      # Panel de chat individual
│   │   │   └── MultiCVChatPanel.tsx  # Chat comparativo
│   │   ├── types/                 # Definiciones de tipos
│   │   └── utils/                 # Utilidades y helpers
│   └── package.json
└── requirements.txt               # Dependencias Python
```

## Extensibilidad

El diseño basado en nodos facilita:

1. **Añadir nuevos nodos** de análisis sin modificar los existentes
2. **Procesamiento paralelo** mediante ejecución asíncrona
3. **Flujos de trabajo alternativos** conectando nodos en diferentes configuraciones
4. **Reutilización de componentes** en diferentes partes del sistema

