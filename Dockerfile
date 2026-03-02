# Imagem base Python
FROM python:3.11-slim

# Metadados
LABEL maintainer="Document Processing Pipeline"
LABEL description="Pipeline de processamento de documentos com LLM"
LABEL version="1.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema (Tesseract OCR + Poppler)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ ./src/
COPY main.py .
COPY .env.example .

# Cria diretórios necessários
RUN mkdir -p /app/data/raw /app/output /app/logs

# Volume para dados e resultados
VOLUME ["/app/data", "/app/output", "/app/logs"]

# Healthcheck (opcional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.llm_client; print('OK')" || exit 1

# Comando padrão
ENTRYPOINT ["python", "main.py"]

# Argumentos padrão (pode sobrescrever)
CMD ["--input-dir", "data/raw", "--output-dir", "output"]
