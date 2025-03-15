# Analizador de Currículum

Sistema de análisis de currículum utilizando IA generativa (Gemini) para evaluar compatibilidad con descripciones de puestos.

## Índice
1. [Arquitectura técnica](#arquitectura-técnica)
2. [Configuración del entorno](#configuración-del-entorno)
3. [Paralelización con Kubernetes](#paralelización-con-kubernetes)
4. [Despliegue completo](#despliegue-completo)
5. [Pruebas de rendimiento](#pruebas-de-rendimiento)
6. [Desarrollo y extensión](#desarrollo-y-extensión)
7. [Troubleshooting](#troubleshooting)

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

## Configuración del Entorno

### Requisitos del Sistema
- Python 3.9+
- Node.js 16+
- Docker
- Kubernetes (minikube para desarrollo)
- API key de Google Gemini

### Configuración Inicial

1. **Clonar el repositorio e instalar dependencias:**

```bash
git clone https://your-repository/workflow_cv.git
cd workflow_cv

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de frontend
cd front
npm install
cd ..
```

2. **Configurar la API key de Gemini:**

Crea un archivo `.env` en la raíz del proyecto:

```bash
echo "GEMINI_API_KEY=\"TU_API_KEY_AQUI\"" > .env
```

3. **Verificar instalación de minikube:**

```bash
minikube version  # Comprobar que está instalado

# Si no está instalado:
# macOS: brew install minikube
# Linux: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## Paralelización con Kubernetes

El sistema está optimizado para procesar múltiples CVs en paralelo utilizando Kubernetes. Los componentes clave para la paralelización son:

### Archivos de Configuración

#### 1. Dockerfile
El Dockerfile configura el contenedor con soporte para procesamiento paralelo:

```Dockerfile
# Extracto clave para paralelización
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "5"]
```

Cada pod ejecuta 5 workers para permitir múltiples peticiones simultáneas, crucial para el paralelismo real.

#### 2. deployment.yaml
Define cómo se desplegarán los pods en Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cv-analyzer
spec:
  replicas: 5  # 5 pods para procesar hasta 5 CVs en paralelo
  # ... resto de configuración
```

**Puntos críticos para el paralelismo:**
- `replicas: 5`: Permite procesar 5 CVs simultáneamente
- Recursos optimizados para evitar limitaciones de CPU/memoria durante análisis intensivo

#### 3. service.yaml
Expone el servicio para que sea accesible:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cv-analyzer-service
spec:
  type: NodePort  # Permite acceso desde fuera de Kubernetes
  # ... resto de configuración
```

### Implementación del Paralelismo en Frontend

El archivo clave es `front/src/App.tsx`, que implementa el procesamiento paralelo:

```typescript
const analysisPromises = files.map((file, index) => 
  sendCVWithRetry(file, jobDesc, index)
);

// Promise.all ejecuta todas las peticiones en paralelo 
const analysisResults = await Promise.all(analysisPromises);
```

La función `sendCVWithRetry` gestiona la comunicación con el backend y reintentos:

```typescript
// Función para enviar un CV con reintentos
const sendCVWithRetry = async (file, jobDesc, index, maxRetries = 2) => {
  // Envía peticiones HTTP al backend y maneja reintentos
  // Ver front/src/App.tsx para detalles completos
};
```

## Despliegue Completo

Para facilitar el despliegue, utilizamos un script automatizado `launch.sh`:

### Uso del Script de Lanzamiento

```bash
# Asegúrate de que el script es ejecutable
chmod +x launch.sh

# Ejecutar el script
./launch.sh
```

### ¿Qué hace launch.sh?

El script automatiza todos estos pasos:

1. Verifica la existencia del archivo `.env`
2. Reinicia minikube completamente para asegurar un entorno limpio
3. Construye la imagen Docker con configuración de procesamiento paralelo
4. Carga la imagen en el registro local de minikube
5. Despliega la aplicación con Kubernetes (deployment, service)
6. Configura el port-forward para acceder al servicio
7. Actualiza la configuración del frontend con la URL del servicio
8. Inicia el frontend en modo desarrollo

### Comandos Manuales (si prefieres no usar el script)

Si prefieres ejecutar los pasos manualmente:

```bash
# 1. Iniciar minikube
minikube start --cpus=4 --memory=6144

# 2. Construir imagen Docker
docker build -t cv-analyzer:latest .

# 3. Cargar imagen en minikube
minikube image load cv-analyzer:latest

# 4. Desplegar en Kubernetes
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 5. Configurar port-forward
kubectl port-forward service/cv-analyzer-service 8000:80 > /dev/null 2>&1 &

# 6. Crear/editar archivo de configuración del frontend
cat > front/src/config.ts << EOF
export const API_URL = 'http://localhost:8000';
EOF

# 7. Iniciar frontend
cd front
npm run dev
```

## Pruebas de Rendimiento

Para verificar que el sistema realmente procesa CVs en paralelo:

### Preparación de Prueba

1. Prepara 3-5 archivos PDF de CV para pruebas
2. Escribe una descripción de puesto en un archivo de texto

### Ejecución de Prueba

1. Inicia la aplicación con el script `launch.sh`
2. Abre la consola del navegador (F12) para ver logs
3. Carga los 3-5 CVs y la descripción de puesto
4. Haz clic en "Analizar CVs"

### Verificación de Paralelismo

Observa los logs en la consola para confirmar:

```
Usando API en: http://localhost:8000
Procesando 3 CVs en paralelo...
Enviando CV 1: Marieta_Escribano_CV.pdf para análisis paralelo
Enviando CV 2: Alejandro_Mora_CV.pdf para análisis paralelo
Enviando CV 3: Carla_Garcia_CV.pdf para análisis paralelo

(... después de un tiempo ...)

CV procesado 1: Marieta_Escribano_CV.pdf - Éxito!
CV procesado 2: Alejandro_Mora_CV.pdf - Éxito!
CV procesado 3: Carla_Garcia_CV.pdf - Éxito!
Todos los CVs procesados en 18.44 segundos
```

**Cómo confirmar el verdadero paralelismo:**
- Los CVs se inician en el mismo tiempo (timestamps cercanos)
- El tiempo total es aproximadamente igual al CV más lento (no a la suma)
- Los logs de Kubernetes muestran actividad simultánea en múltiples pods

Para ver la actividad de los pods, como solo permite 5, le ponemos un maximo de 10:
```bash
kubectl logs -f -l app=cv-analyzer --all-containers --max-log-requests=10
```

## Desarrollo y Extensión

### Estructura Completa de Directorios

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
│   │       ├── cv_analyzer_workflow.py  # Implementación del workflow
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
│   │   ├── App.tsx                # Componente principal
│   │   ├── config.ts              # Configuración de API URL
│   │   ├── types/                 # Definiciones de tipos
│   │   └── utils/                 # Utilidades y helpers
│   └── package.json
├── Dockerfile                     # Configuración de contenedor
├── deployment.yaml                # Configuración de despliegue Kubernetes
├── service.yaml                   # Configuración de servicio Kubernetes
├── launch.sh                      # Script de despliegue automatizado
├── requirements.txt               # Dependencias Python
└── .env                           # Variables de entorno (API keys)
```

### Añadir un Nuevo Nodo al Workflow

Para extender el sistema con un nuevo nodo:

1. Crear una nueva clase que herede de `BaseNode`:

```python
# backend/app/services/nodes/new_feature_node.py
from .base_node import BaseNode
from pydantic import BaseModel
from typing import Dict, Any

class NewFeatureInput(BaseModel):
    """Define la entrada del nuevo nodo"""
    # Campos necesarios para este nodo

class NewFeatureOutput(BaseModel):
    """Define la salida del nuevo nodo"""
    # Resultados que producirá este nodo

class NewFeatureNode(BaseNode[NewFeatureInput, NewFeatureOutput, Dict[str, Any]]):
    """Implementación del nuevo nodo"""
    
    async def process(self, input_data: NewFeatureInput, context: Dict[str, Any]) -> NewFeatureOutput:
        # Implementar lógica de procesamiento
        # ...
        return NewFeatureOutput(...)
```

2. Modificar el workflow para incluir el nuevo nodo:

```python
# En backend/app/services/cv_analyzer_workflow.py

from .nodes import NewFeatureNode, NewFeatureInput

# Inicializar el nodo
new_feature_node = NewFeatureNode()

# Añadir al workflow
workflow_manager.add_node(new_feature_node)

# Conectar con el flujo existente
workflow_manager.connect(skills_evaluator_node, new_feature_node)

# Modificar analyze_cv para usar el nuevo nodo
# ...
```

## Troubleshooting

### Problemas de Paralelismo

Si el procesamiento no es paralelo, verifica:

1. **Configuración de workers en Dockerfile**:
   ```bash
   grep "workers" Dockerfile  # Debe ser > 1
   ```

2. **Número de réplicas en deployment.yaml**:
   ```bash
   grep "replicas:" deployment.yaml  # Debe ser >= número de CVs a procesar
   ```

3. **Implementación correcta en App.tsx**:
   ```bash
   grep "Promise.all" front/src/App.tsx  # Debe usar Promise.all para paralelismo
   ```

4. **Logs de Kubernetes para ver distribución**:
   ```bash
   kubectl logs -f -l app=cv-analyzer
   ```

### Problemas con minikube

Si encuentras errores con minikube:

1. **Reinicia completamente minikube**:
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=6144
   ```

2. **Verificar estado de minikube**:
   ```bash
   minikube status
   ```

3. **Problema con Docker en macOS**:
   En macOS con Docker Desktop, a veces el servicio necesita port-forward en lugar de NodePort:
   ```bash
   # Editar launch.sh para usar esta línea:
   kubectl port-forward service/cv-analyzer-service 8000:80 > /dev/null 2>&1 &
   ```

### Problemas de Conexión al Backend

Si el frontend no puede conectar con el backend:

1. **Verificar service.yaml**:
   ```bash
   cat service.yaml  # Debe usar type: NodePort
   ```

2. **Comprobar URL en config.ts**:
   ```bash
   cat front/src/config.ts  # Debe apuntar a la URL correcta
   ```

3. **Verificar que los pods están ejecutándose**:
   ```bash
   kubectl get pods -l app=cv-analyzer
   ```

4. **Probar acceso directo al servicio**:
   ```bash
   curl $(minikube service cv-analyzer-service --url)
   ```

### Problemas de API Key de Gemini

Si hay errores de API key:

1. **Verificar .env**:
   ```bash
   cat .env  # Debe contener GEMINI_API_KEY correcta
   ```

2. **Verificar que se copia al contenedor**:
   ```bash
   grep "COPY .env" Dockerfile  # Debe estar presente
   ```

3. **Probar API key manualmente**:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="TU_API_KEY")
   model = genai.GenerativeModel('gemini-2.0-flash')
   response = model.generate_content("Hello")
   print(response.text)
   ```

## Métricas de Rendimiento

Para medir el rendimiento del sistema:

1. **Tiempo de procesamiento paralelo** (desde el frontend):
   - Los logs muestran el tiempo total y tiempo por CV

2. **Tiempo de ejecución detallado** (desde el backend):
   - Cada nodo registra su tiempo de ejecución en los metadatos
   - Ejemplo para obtener estos tiempos:

   ```python
   # En un endpoint de depuración
   @router.get("/performance-metrics/")
   async def get_performance_metrics():
       workflow_metadata = cv_analyzer_service.get_workflow_metadata()
       node_times = {}
       for node_name, metadata in workflow_metadata.node_metadata.items():
           node_times[node_name] = metadata.execution_time_ms
       return {
           "total_time_ms": workflow_metadata.execution_time_ms,
           "node_times": node_times
       }
   ```

3. **Monitorear recursos de Kubernetes**:
   ```bash
   kubectl top pods
   ```

---

Este sistema ha sido optimizado para procesamiento paralelo de CVs utilizando una arquitectura de nodos, Kubernetes y React. Para más información, contacta al equipo de desarrollo.

