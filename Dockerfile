# Imagen base ligera
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para compilar PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    liblcms2-dev \
    libffi-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero para aprovechar la caché
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el archivo .env
COPY .env .

# Copiar el código de backend
COPY backend/ .

# Exponer puerto de FastAPI
EXPOSE 8000

# Iniciar la aplicación con múltiples workers para permitir paralelismo
# workers=5 permite hasta 5 solicitudes simultaneas por pod
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "5"]
