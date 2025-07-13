# CV Analyzer

AI-powered curriculum vitae analysis system utilizing generative AI (Gemini) to evaluate compatibility with job descriptions.

## Table of Contents
1. [Technical Architecture](#technical-architecture)
2. [Environment Setup](#environment-setup)
3. [Kubernetes Parallelization](#kubernetes-parallelization)
4. [Complete Deployment](#complete-deployment)
5. [Performance Testing](#performance-testing)
6. [Development and Extension](#development-and-extension)
7. [Troubleshooting](#troubleshooting)

## Technical Architecture

The system implements a modular node-based architecture for CV processing, enabling structured and extensible data flow.

### Core: Processing Nodes

The fundamental unit of the system is the `BaseNode`, a generic abstract class that defines the base behavior for all nodes:

```python
class BaseNode(Generic[InputT, OutputT, ContextT], ABC):
    async def process(self, input_data: InputT, context: ContextT) -> OutputT:
        pass
        
    async def execute(self, input_data: InputT, context: ContextT = None) -> tuple[OutputT, NodeMetadata]:
        # Implementation with measurement, caching, and error handling
```

### Primary Analysis Nodes

- **ExtractorNode**: Extracts text and metadata from PDF files
  - Input: `ExtractorInput(file_path, mime_type)`
  - Output: `CVDocument(text, filename, file_size, extraction_date, mime_type)`

- **ClassifierNode**: Categorizes text into structured sections
  - Input: `CVDocument`
  - Output: `ClassifiedCV(nombre, correo, telefono, ubicacion, educacion_texto, experiencia_texto, etc.)`

- **SkillsEvaluatorNode**: Analyzes and evaluates skills against requirements
  - Input: `SkillsEvaluatorInput(classified_cv, job_description)`
  - Output: `SkillsEvaluation(habilidades_tecnicas, habilidades_blandas, puntuacion_general, etc.)`

- **ChatNode**: Enables conversational interaction with analysis results
  - Input: `ChatInput(session_id, message, cv_data, job_description, etc.)`
  - Output: `ChatOutput(response, session_id)`

### Workflow Manager

The `WorkflowManager` class orchestrates node execution:

```python
workflow = WorkflowManager("CVAnalysisWorkflow")
workflow.add_node(extractor_node)
workflow.add_node(classifier_node)
workflow.add_node(skills_evaluator_node)

workflow.connect("extractor_node", "classifier_node")
workflow.connect("classifier_node", "skills_evaluator_node")

result = await workflow.execute("extractor_node", initial_input, context)
```

Manager features:
- Sequential or parallel node execution
- Execution metadata tracking
- State system for progress monitoring
- Cache system for intermediate results

### Data Models (Pydantic)

The project extensively uses Pydantic models to ensure typed and validated data transfer:

#### Core CV Analysis Models
```python
class CVDocument(BaseModel):
    """Extracted text and CV metadata"""
    text: str
    filename: str
    file_size: int
    extraction_date: datetime
    mime_type: str

class ClassifiedCV(BaseModel):
    """Information categorized by sections"""
    nombre: Optional[str]
    correo: Optional[str]
    # Additional structured fields...

class SkillsEvaluation(BaseModel):
    """Skills evaluation"""
    habilidades_tecnicas: List[HabilidadEvaluada]
    habilidades_blandas: List[HabilidadEvaluada]
    puntuacion_general: float
    # Additional evaluation fields...
```

#### Chat Models
```python
class ChatSession(BaseModel):
    """Chat session with history and context"""
    session_id: str
    messages: List[ChatMessage]
    cv_data: Optional[Dict[str, Any]]
    job_description: Optional[str]
    # Additional context fields...
```

## API and Endpoints

The system exposes two main endpoint groups:

### CV Analysis (cv_router.py)
- POST `/analyze-cv/` - Analyzes a CV against a job description
- GET `/workflow-status/` - Retrieves workflow status
- POST `/clear-caches/` - Clears node caches

### Chat Interaction (chat_router.py)
- POST `/chat/sessions/` - Creates a new chat session for a CV
- POST `/chat/multi-sessions/` - Creates session with multiple CVs for comparison
- POST `/chat/messages/` - Sends messages to a chat session
- GET `/chat/sessions/{session_id}` - Retrieves session information
- DELETE `/chat/sessions/{session_id}` - Deletes a session

## React User Interface

The interface is built with React and TypeScript, featuring modular components:

### Core Components
- **UploadForm** - CV and job description upload
- **ResultsList** - Ordered list of analysis results
- **DetailedAnalysis** - Detailed analysis visualization
- **VisualSummary** - Visual summary with compatibility charts
- **ChatPanel** - Conversational interface for a single CV
- **MultiCVChatPanel** - Comparative conversational interface for multiple CVs

## Additional Technical Features

- **Integrated caching** in nodes for performance optimization
- **Execution time measurement** for performance analysis
- **Metadata system** for execution tracking
- **Asynchronous processing** with asyncio
- **Gemini AI integration** for advanced semantic analysis
- **Persistent chat sessions** for interactive querying

## Technologies

- **Backend**: FastAPI, Pydantic, PyMuPDF, AsyncIO
- **ML Processing**: Google Gemini 2.0 Flash (API)
- **Frontend**: React, TypeScript, Tailwind CSS
- **Development Tools**: Vite, ESLint

## Installation

1. Clone the repository
2. Create a `.env` file based on `.env.example` with your Gemini API key
3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
cd front
npm install
```

## Development and Execution

### Start the backend

```bash
cd backend
uvicorn main:app --reload
```

### Start the frontend

```bash
cd front
npm run dev
```

### Access the application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## File Architecture

```
/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── node_schemas.py    # Data models for nodes
│   │   │   └── schemas.py         # API and response models
│   │   ├── routers/
│   │   │   ├── cv_router.py       # CV analysis endpoints
│   │   │   └── chat_router.py     # Chat interaction endpoints
│   │   └── services/
│   │       ├── cv_analyzer.py     # Analysis service
│   │       ├── chat_service.py    # Conversation service
│   │       └── nodes/             # Node implementations
│   │           ├── base_node.py   # Abstract base class
│   │           ├── extractor_node.py
│   │           ├── classifier_node.py
│   │           ├── skills_evaluator_node.py
│   │           ├── chat_node.py
│   │           └── workflow.py    # Workflow manager
│   └── main.py                    # Entry point
├── front/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── UploadForm.tsx     # File upload
│   │   │   ├── ResultsList.tsx    # Results list
│   │   │   ├── DetailedAnalysis.tsx  # Detailed analysis
│   │   │   ├── VisualSummary.tsx  # Visual summary
│   │   │   ├── ChatPanel.tsx      # Individual chat panel
│   │   │   └── MultiCVChatPanel.tsx  # Comparative chat
│   │   ├── types/                 # Type definitions
│   │   └── utils/                 # Utilities and helpers
│   └── package.json
└── requirements.txt               # Python dependencies
```

## Extensibility

The node-based design facilitates:

1. **Adding new analysis nodes** without modifying existing ones
2. **Parallel processing** through asynchronous execution
3. **Alternative workflows** by connecting nodes in different configurations
4. **Component reuse** across different parts of the system

## Environment Setup

### System Requirements
- Python 3.9+
- Node.js 16+
- Docker
- Kubernetes (minikube for development)
- Google Gemini API key

### Initial Configuration

1. **Clone the repository and install dependencies:**

```bash
git clone https://your-repository/workflow_cv.git
cd workflow_cv

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd front
npm install
cd ..
```

2. **Configure the Gemini API key:**

Create a `.env` file in the project root:

```bash
echo "GEMINI_API_KEY=\"YOUR_API_KEY_HERE\"" > .env
```

3. **Verify minikube installation:**

```bash
minikube version  # Check if installed

# If not installed:
# macOS: brew install minikube
# Linux: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## Kubernetes Parallelization

The system is optimized to process multiple CVs in parallel using Kubernetes. The key components for parallelization are:

### Configuration Files

#### 1. Dockerfile
The Dockerfile configures the container with support for parallel processing:

```Dockerfile
# Key extract for parallelization
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "5"]
```

Each pod runs 5 workers to allow multiple simultaneous requests, crucial for real parallelism.

#### 2. deployment.yaml
Defines how pods will be deployed in Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cv-analyzer
spec:
  replicas: 5  # 5 pods to process up to 5 CVs in parallel
  # ... rest of configuration
```

**Critical points for parallelism:**
- `replicas: 5`: Allows processing 5 CVs simultaneously
- Optimized resources to avoid CPU/memory limitations during intensive analysis

#### 3. service.yaml
Exposes the service for accessibility:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cv-analyzer-service
spec:
  type: NodePort  # Allows access from outside Kubernetes
  # ... rest of configuration
```

### Frontend Parallelism Implementation

The key file is `front/src/App.tsx`, which implements parallel processing:

```typescript
const analysisPromises = files.map((file, index) => 
  sendCVWithRetry(file, jobDesc, index)
);

// Promise.all executes all requests in parallel 
const analysisResults = await Promise.all(analysisPromises);
```

The `sendCVWithRetry` function manages backend communication and retries:

```typescript
// Function to send a CV with retries
const sendCVWithRetry = async (file, jobDesc, index, maxRetries = 2) => {
  // Sends HTTP requests to backend and handles retries
  // See front/src/App.tsx for complete details
};
```

## Complete Deployment

To facilitate deployment, we use an automated script `launch.sh`:

### Using the Launch Script

```bash
# Ensure the script is executable
chmod +x launch.sh

# Execute the script
./launch.sh
```

### What does launch.sh do?

The script automates all these steps:

1. Verifies the existence of the `.env` file
2. Restarts minikube completely to ensure a clean environment
3. Builds the Docker image with parallel processing configuration
4. Loads the image into minikube's local registry
5. Deploys the application with Kubernetes (deployment, service)
6. Configures port-forward to access the service
7. Updates frontend configuration with the service URL
8. Starts the frontend in development mode

### Manual Commands (if you prefer not to use the script)

If you prefer to execute the steps manually:

```bash
# 1. Start minikube
minikube start --cpus=4 --memory=6144

# 2. Build Docker image
docker build -t cv-analyzer:latest .

# 3. Load image into minikube
minikube image load cv-analyzer:latest

# 4. Deploy to Kubernetes
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 5. Configure port-forward
kubectl port-forward service/cv-analyzer-service 8000:80 > /dev/null 2>&1 &

# 6. Create/edit frontend configuration file
cat > front/src/config.ts << EOF
export const API_URL = 'http://localhost:8000';
EOF

# 7. Start frontend
cd front
npm run dev
```

## Performance Testing

To verify that the system truly processes CVs in parallel:

### Test Preparation

1. Prepare 3-5 PDF CV files for testing
2. Write a job description in a text file

### Test Execution

1. Start the application with the `launch.sh` script
2. Open the browser console (F12) to view logs
3. Upload the 3-5 CVs and job description
4. Click "Analyze CVs"

### Parallelism Verification

Observe the console logs to confirm:

```
Using API at: http://localhost:8000
Processing 3 CVs in parallel...
Sending CV 1: Marieta_Escribano_CV.pdf for parallel analysis
Sending CV 2: Alejandro_Mora_CV.pdf for parallel analysis
Sending CV 3: Carla_Garcia_CV.pdf for parallel analysis

(... after some time ...)

CV processed 1: Marieta_Escribano_CV.pdf - Success!
CV processed 2: Alejandro_Mora_CV.pdf - Success!
CV processed 3: Carla_Garcia_CV.pdf - Success!
All CVs processed in 18.44 seconds
```

**How to confirm true parallelism:**
- CVs start at the same time (close timestamps)
- Total time is approximately equal to the slowest CV (not the sum)
- Kubernetes logs show simultaneous activity across multiple pods

To view pod activity, since it only allows 5, we set a maximum of 10:
```bash
kubectl logs -f -l app=cv-analyzer --all-containers --max-log-requests=10
```

## Development and Extension

### Complete Directory Structure

```
/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── node_schemas.py    # Data models for nodes
│   │   │   └── schemas.py         # API and response models
│   │   ├── routers/
│   │   │   ├── cv_router.py       # CV analysis endpoints
│   │   │   └── chat_router.py     # Chat interaction endpoints
│   │   └── services/
│   │       ├── cv_analyzer.py     # Analysis service
│   │       ├── cv_analyzer_workflow.py  # Workflow implementation
│   │       ├── chat_service.py    # Conversation service
│   │       └── nodes/             # Node implementations
│   │           ├── base_node.py   # Abstract base class
│   │           ├── extractor_node.py
│   │           ├── classifier_node.py
│   │           ├── skills_evaluator_node.py
│   │           ├── chat_node.py
│   │           └── workflow.py    # Workflow manager
│   └── main.py                    # Entry point
├── front/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── UploadForm.tsx     # File upload
│   │   │   ├── ResultsList.tsx    # Results list
│   │   │   ├── DetailedAnalysis.tsx  # Detailed analysis
│   │   │   ├── VisualSummary.tsx  # Visual summary
│   │   │   ├── ChatPanel.tsx      # Individual chat panel
│   │   │   └── MultiCVChatPanel.tsx  # Comparative chat
│   │   ├── App.tsx                # Main component
│   │   ├── config.ts              # API URL configuration
│   │   ├── types/                 # Type definitions
│   │   └── utils/                 # Utilities and helpers
│   └── package.json
├── Dockerfile                     # Container configuration
├── deployment.yaml                # Kubernetes deployment configuration
├── service.yaml                   # Kubernetes service configuration
├── launch.sh                      # Automated deployment script
├── requirements.txt               # Python dependencies
└── .env                           # Environment variables (API keys)
```

### Adding a New Node to the Workflow

To extend the system with a new node:

1. Create a new class that inherits from `BaseNode`:

```python
# backend/app/services/nodes/new_feature_node.py
from .base_node import BaseNode
from pydantic import BaseModel
from typing import Dict, Any

class NewFeatureInput(BaseModel):
    """Define the new node's input"""
    # Required fields for this node

class NewFeatureOutput(BaseModel):
    """Define the new node's output"""
    # Results this node will produce

class NewFeatureNode(BaseNode[NewFeatureInput, NewFeatureOutput, Dict[str, Any]]):
    """New node implementation"""
    
    async def process(self, input_data: NewFeatureInput, context: Dict[str, Any]) -> NewFeatureOutput:
        # Implement processing logic
        # ...
        return NewFeatureOutput(...)
```

2. Modify the workflow to include the new node:

```python
# In backend/app/services/cv_analyzer_workflow.py

from .nodes import NewFeatureNode, NewFeatureInput

# Initialize the node
new_feature_node = NewFeatureNode()

# Add to workflow
workflow_manager.add_node(new_feature_node)

# Connect with existing flow
workflow_manager.connect(skills_evaluator_node, new_feature_node)

# Modify analyze_cv to use the new node
# ...
```

## Troubleshooting

### Parallelism Issues

If processing is not parallel, verify:

1. **Worker configuration in Dockerfile**:
   ```bash
   grep "workers" Dockerfile  # Should be > 1
   ```

2. **Number of replicas in deployment.yaml**:
   ```bash
   grep "replicas:" deployment.yaml  # Should be >= number of CVs to process
   ```

3. **Correct implementation in App.tsx**:
   ```bash
   grep "Promise.all" front/src/App.tsx  # Should use Promise.all for parallelism
   ```

4. **Kubernetes logs to see distribution**:
   ```bash
   kubectl logs -f -l app=cv-analyzer
   ```

### Minikube Issues

If you encounter errors with minikube:

1. **Restart minikube completely**:
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=6144
   ```

2. **Check minikube status**:
   ```bash
   minikube status
   ```

3. **Docker issue on macOS**:
   On macOS with Docker Desktop, sometimes the service needs port-forward instead of NodePort:
   ```bash
   # Edit launch.sh to use this line:
   kubectl port-forward service/cv-analyzer-service 8000:80 > /dev/null 2>&1 &
   ```

### Backend Connection Issues

If the frontend cannot connect to the backend:

1. **Verify service.yaml**:
   ```bash
   cat service.yaml  # Should use type: NodePort
   ```

2. **Check URL in config.ts**:
   ```bash
   cat front/src/config.ts  # Should point to the correct URL
   ```

3. **Verify pods are running**:
   ```bash
   kubectl get pods -l app=cv-analyzer
   ```

4. **Test direct service access**:
   ```bash
   curl $(minikube service cv-analyzer-service --url)
   ```

### Gemini API Key Issues

If there are API key errors:

1. **Verify .env**:
   ```bash
   cat .env  # Should contain correct GEMINI_API_KEY
   ```

2. **Verify it's copied to the container**:
   ```bash
   grep "COPY .env" Dockerfile  # Should be present
   ```

3. **Test API key manually**:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="YOUR_API_KEY")
   model = genai.GenerativeModel('gemini-2.0-flash')
   response = model.generate_content("Hello")
   print(response.text)
   ```

## Performance Metrics

To measure system performance:

1. **Parallel processing time** (from frontend):
   - Logs show total time and time per CV

2. **Detailed execution time** (from backend):
   - Each node records its execution time in metadata
   - Example to obtain these times:

   ```python
   # In a debug endpoint
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

3. **Monitor Kubernetes resources**:
   ```bash
   kubectl top pods
   ```

---

This system has been optimized for parallel CV processing using a node-based architecture, Kubernetes, and React. For more information, contact the development team.

