#!/bin/bash

# Colores para mejor visualización
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Iniciando sistema de análisis de CVs ===${NC}"

# 0. Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: No se encontró el archivo .env${NC}"
    echo -e "Por favor, crea un archivo .env en la raíz del proyecto con la siguiente estructura:"
    echo -e "#API KEYS"
    echo -e "GEMINI_API_KEY=\"tu_api_key_aqui\""
    exit 1
fi

# 0.1 Reiniciar completamente minikube
echo -e "${YELLOW}Reiniciando Minikube completamente para asegurar configuración limpia...${NC}"
minikube delete
minikube start --cpus=6 --memory=7000 # Aumentado a 6 CPUs y 8GB RAM para 10 pods
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al iniciar Minikube${NC}"
    exit 1
fi
echo -e "${GREEN}Minikube iniciado correctamente${NC}"

# 1. Limpiar cualquier despliegue anterior
echo -e "${YELLOW}Limpiando despliegues anteriores...${NC}"
kubectl delete deployment cv-analyzer 2>/dev/null
kubectl delete service cv-analyzer-service 2>/dev/null

# 2. Construir la imagen Docker con soporte para procesamiento paralelo
echo -e "${YELLOW}Construyendo imagen Docker con soporte para procesamiento paralelo...${NC}"
docker build -t cv-analyzer:latest .
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al construir la imagen Docker${NC}"
    exit 1
fi
echo -e "${GREEN}Imagen Docker construida exitosamente${NC}"

# 3. Cargar la imagen en minikube
echo -e "${YELLOW}Cargando imagen en Minikube...${NC}"
minikube image load cv-analyzer:latest
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al cargar la imagen en Minikube${NC}"
    exit 1
fi
echo -e "${GREEN}Imagen cargada en Minikube correctamente${NC}"

# 4. Verificar que existan los archivos de configuración
if [ ! -f "deployment.yaml" ] || [ ! -f "service.yaml" ]; then
    echo -e "${RED}Error: Faltan archivos de configuración${NC}"
    echo -e "Verificando archivos:"
    echo -e "deployment.yaml: $([ -f "deployment.yaml" ] && echo "Existe" || echo "No existe")"
    echo -e "service.yaml: $([ -f "service.yaml" ] && echo "Existe" || echo "No existe")"
    exit 1
fi

# 5. Aplicar configuración a Kubernetes
echo -e "${YELLOW}Aplicando configuración a Kubernetes...${NC}"
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
if [ $? -ne 0 ]; then
    echo -e "${RED}Error al aplicar configuración Kubernetes${NC}"
    exit 1
fi
echo -e "${GREEN}Configuración de Kubernetes aplicada correctamente${NC}"

# 6. Esperar a que los pods estén listos
echo -e "${YELLOW}Esperando a que los pods estén listos...${NC}"
kubectl rollout status deployment/cv-analyzer --timeout=180s  # Aumentado a 180s para 10 pods
if [ $? -ne 0 ]; then
    echo -e "${RED}Advertencia: Tiempo de espera agotado para los pods${NC}"
    echo -e "${YELLOW}Continuando de todos modos...${NC}"
fi

# 7. Configurar acceso a múltiples pods simultáneamente
echo -e "${YELLOW}Configurando acceso a múltiples pods simultáneamente...${NC}"
# Usar NodePort y obtener la URL directamente
minikube service cv-analyzer-service --url > service_url.txt &
sleep 3  # Dar tiempo para que se genere la URL
kill $! 2>/dev/null

# Verificar si se generó la URL correctamente
if [ -s service_url.txt ]; then
    SERVICE_URL=$(cat service_url.txt)
    echo -e "${GREEN}Servicio accesible en: ${SERVICE_URL}${NC}"
else
    # Fallback al port-forward tradicional si falla minikube service
    echo -e "${YELLOW}Fallback: usando port-forward...${NC}"
    kubectl port-forward svc/cv-analyzer-service 8000:80 > /dev/null 2>&1 &
    PORT_FORWARD_PID=$!
    SERVICE_URL="http://localhost:8000"
    echo -e "${GREEN}Servicio accesible en: ${SERVICE_URL}${NC}"
fi

# 8. Actualizar la URL de la API en el frontend
cat > front/src/config.ts << EOF
// Configuración generada automáticamente
export const API_URL = '${SERVICE_URL}';
EOF

echo -e "${GREEN}Archivo de configuración del frontend actualizado${NC}"

# 9. Mostrar información sobre los pods
echo -e "${YELLOW}Pods disponibles:${NC}"
kubectl get pods -l app=cv-analyzer

# 10. Instalar dependencias e iniciar el frontend
echo -e "${YELLOW}Iniciando el frontend...${NC}"
cd front

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Instalando dependencias del frontend...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error al instalar dependencias del frontend${NC}"
        # Limpiar port-forward si existe
        if [ ! -z ${PORT_FORWARD_PID+x} ]; then
            kill $PORT_FORWARD_PID 2>/dev/null
        fi
        exit 1
    fi
fi

# Iniciar el frontend
echo -e "${YELLOW}Lanzando aplicación frontend...${NC}"
npm run dev

# Limpiar al salir
if [ ! -z ${PORT_FORWARD_PID+x} ]; then
    kill $PORT_FORWARD_PID 2>/dev/null
fi
echo -e "${GREEN}¡Sistema cerrado correctamente!${NC}"
