# Stage 1: Base image with Python and Poetry
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    DEBIAN_FRONTEND=noninteractive

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
# Use retries and handle network issues gracefully
RUN set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    for i in 1 2 3; do \
        echo "Attempting apt-get update (attempt $i/3)..."; \
        apt-get update && break || sleep $((i * 5)); \
    done; \
    apt-get install -y --no-install-recommends --fix-missing \
        curl \
        build-essential \
        libpq-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libfontconfig1 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        shared-mime-info \
    || { \
        echo "Package installation failed, attempting recovery..."; \
        apt-get clean; \
        apt-get update; \
        apt-get install -y --no-install-recommends --fix-missing \
            curl \
            build-essential \
            libpq-dev \
            libpango-1.0-0 \
            libpangoft2-1.0-0 \
            libfontconfig1 \
            libcairo2 \
            libgdk-pixbuf2.0-0 \
            shared-mime-info; \
    }; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set work directory
WORKDIR /app

# Stage 2: Dependencies
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (production only)
RUN poetry install --no-root --only main

# Stage 3: Production image
FROM base AS production

# Copy installed dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

