FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos primeiro para aproveitar o cache de camadas
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p uploads results logs models_repository

# Copiar código-fonte
COPY . .

# Expor porta
EXPOSE 8000

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/uploads
ENV RESULTS_DIR=/app/results
ENV LOGS_DIR=/app/logs
ENV MODELS_DIR=/app/models_repository
ENV HOST=0.0.0.0
ENV PORT=8000

# Comando para iniciar o serviço
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
