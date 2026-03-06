FROM python:3.12-slim AS base

# System dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# Copy application
COPY src/ src/
COPY frontend/ frontend/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY data/samples/ data/samples/

# Create data directories
RUN mkdir -p data/uploads

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "docai.main:app", "--host", "0.0.0.0", "--port", "8000"]
