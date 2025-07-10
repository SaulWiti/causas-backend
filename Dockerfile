# Utiliza una imagen base de Python 3.11
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Expone el puerto que usa FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT", "--reload"]
