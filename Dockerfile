# =====================================================================
# Imagen para la aplicación Zimbra CRM (FastAPI + SQLAlchemy + PyMySQL).
# Base: Python 3.11 slim. Se incluyen herramientas de compilación porque
# `cryptography` y `pymysql` pueden necesitarlas en arquitecturas sin
# wheel precompilado (arm64, p. ej.).
# =====================================================================
FROM python:3.11-slim

# Variables de entorno para Python en contenedores.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias de sistema mínimas. Se eliminan listas de apt al final
# para mantener la imagen pequeña.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Capa de dependencias (primero requirements para aprovechar el caché).
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Código de la aplicación.
COPY app/       ./app/
COPY frontend/  ./frontend/
COPY scripts/   ./scripts/
COPY sql/       ./sql/

EXPOSE 8000

# Comando por defecto. docker-compose lo sobrescribe para añadir --reload.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
