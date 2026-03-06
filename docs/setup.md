# Setup Guide

## Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose** (recommended)
- **uv** ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Tesseract OCR** (for local development without Docker)

---

## Option A: Docker (Recommended)

The fastest way to get everything running:

```bash
# 1. Clone the repository
git clone https://github.com/adrianopsf/document-intelligence-pipeline.git
cd document-intelligence-pipeline

# 2. Configure environment
cp .env.example .env
# Edit .env: set LLM_API_KEY to your OpenAI key (or Ollama URL)

# 3. Start all services
docker-compose up --build -d

# 4. Check services
docker-compose ps

# 5. Open the app
# Browser: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Stopping Services

```bash
docker-compose down          # Stop (keep data)
docker-compose down -v       # Stop and remove volumes
```

---

## Option B: Local Development

### 1. Install System Dependencies

**macOS:**
```bash
brew install tesseract uv
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
- Install Tesseract from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
- Set `TESSERACT_CMD` in `.env`
- Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

### 2. Start Infrastructure

```bash
# Start PostgreSQL and Qdrant via Docker
docker-compose up -d postgres qdrant
```

### 3. Install Python Dependencies

```bash
uv sync --all-extras
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run the App

```bash
make run
# Or: uv run uvicorn docai.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Run Tests

```bash
make test
```

---

## LLM Configuration

### OpenAI
```env
LLM_API_KEY=sk-your-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### Ollama (Local)
```env
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2
```

### vLLM / LiteLLM
```env
LLM_API_KEY=your-key
LLM_BASE_URL=http://your-server:8080/v1
LLM_MODEL=your-model
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tesseract not found | Install Tesseract or set `TESSERACT_CMD` in `.env` |
| PostgreSQL connection refused | Ensure PostgreSQL is running on port 5432 |
| Qdrant connection refused | Ensure Qdrant is running on port 6333 |
| LLM errors | Check `LLM_API_KEY` and `LLM_BASE_URL` in `.env` |
| Upload fails | Check `MAX_UPLOAD_SIZE_MB` and file type is supported |
