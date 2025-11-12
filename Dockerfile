# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start command (Railway will set PORT env var)
# Usar sh -c para expandir a variável PORT corretamente
# Adicionar --workers 1 para produção
CMD sh -c "echo '🚀 Iniciando servidor na porta ${PORT:-8000}' && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"

