<div align="center">

# 📄 Document Intelligence Pipeline

[![CI](https://github.com/adrianopsf/document-intelligence-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianopsf/document-intelligence-pipeline/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](./docker-compose.yml)

**Production-grade document processing pipeline with OCR, structured extraction, RAG, and semantic search.**

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [API Reference](./docs/api.md) · [Setup Guide](./docs/setup.md)

</div>

---

## 🎯 What This Does

This pipeline ingests business documents (contracts, invoices, financial reports, legal docs, receipts), processes them through a multi-stage pipeline, and exposes structured data and Q&A capabilities through a REST API.

```
Document Upload → OCR/Text Extraction → Classification → Chunking → Embedding → Vector Indexing → Structured Extraction
                                                                                                          ↓
                                                                              Q&A with RAG ← Semantic Search
```

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **OCR** | Native PDF text + Tesseract OCR fallback for scanned docs |
| **Classification** | Auto-detect document type (contract, invoice, financial, legal, receipt) |
| **Structured Extraction** | LLM-powered extraction of key fields (names, dates, amounts, etc.) |
| **RAG Q&A** | Ask questions about documents with grounded, cited answers |
| **Semantic Search** | Vector-based similarity search across document chunks |
| **Export** | JSON and CSV export of extraction results |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Application                  │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Upload   │ Jobs     │ Extract  │ RAG Q&A  │ Export      │
│ API      │ API      │ API      │ API      │ API         │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                   Service Layer                          │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ OCR      │Classifier│ Chunker  │ Embedder │ Extractor   │
│(PyMuPDF  │(Keyword  │(Sentence │(sentence-│(LLM + JSON  │
│+Tesseract│ heuristic│ boundary)│transform)│ schema)     │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│              Pipeline Orchestrator                       │
├─────────────────────────┬───────────────────────────────┤
│      PostgreSQL         │         Qdrant                │
│   (metadata, fields,    │    (vector embeddings,        │
│    jobs, audit logs)    │     semantic search)          │
└─────────────────────────┴───────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- (Optional) Tesseract OCR for local development

### Docker (Recommended)

```bash
# Clone
git clone https://github.com/adrianopsf/document-intelligence-pipeline.git
cd document-intelligence-pipeline

# Configure
cp .env.example .env
# Edit .env with your LLM API key (OpenAI, Ollama, etc.)

# Generate sample PDFs for testing
make samples

# Start everything
docker-compose up --build -d

# Open the UI
open http://localhost:8000
```

### Local Development

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Start PostgreSQL and Qdrant (via Docker)
docker-compose up -d postgres qdrant

# Run the API server
make run

# Run tests
make test
```

---

## 📋 API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/documents/upload` | POST | Upload a document |
| `/api/v1/documents` | GET | List all documents |
| `/api/v1/documents/{id}` | GET | Document detail with pages |
| `/api/v1/jobs/{id}` | GET | Processing job status |
| `/api/v1/extraction/{id}` | GET | Extracted fields |
| `/api/v1/rag/query` | POST | Ask a question (RAG) |
| `/api/v1/export/{id}/json` | GET | Export as JSON |
| `/api/v1/export/{id}/csv` | GET | Export as CSV |

Full API docs available at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc`.

---

## 🧰 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **API** | FastAPI + Uvicorn | Async, auto-OpenAPI, production-ready |
| **Database** | PostgreSQL + SQLAlchemy 2.0 | Robust metadata store with async support |
| **Vector Store** | Qdrant | Dedicated vector DB, excellent filtering |
| **OCR** | PyMuPDF + Tesseract | Free, no API keys, swappable engines |
| **Embeddings** | sentence-transformers | Local inference, no API dependency |
| **LLM** | OpenAI-compatible API | Works with OpenAI, Ollama, vLLM, etc. |
| **Migrations** | Alembic | Industry standard for SQLAlchemy |
| **Package Manager** | uv | Fast, modern Python tooling |
| **Container** | Docker + Compose | Full-stack orchestration |
| **CI/CD** | GitHub Actions | Automated lint, test, and Docker build |

---

## 📁 Project Structure

```
document-intelligence-pipeline/
├── src/docai/                  # Main application package
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Pydantic settings
│   ├── database.py             # Async SQLAlchemy engine
│   ├── api/                    # Route handlers
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic (OCR, RAG, pipeline)
│   └── core/                   # Cross-cutting (logging, errors, LLM)
├── frontend/                   # Static web UI
├── tests/                      # Unit and integration tests
├── alembic/                    # Database migrations
├── data/samples/               # Demo documents
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD
├── docker-compose.yml          # Full stack orchestration
├── Dockerfile                  # Application container
└── pyproject.toml              # Python project configuration
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_ocr.py -v
```

---

## 📖 Documentation

- **[Architecture](./ARCHITECTURE.md)** — System design and component overview
- **[API Reference](./docs/api.md)** — Full endpoint documentation
- **[Setup Guide](./docs/setup.md)** — Detailed installation and configuration
- **[Technical Decisions](./docs/decisions.md)** — Trade-offs and design rationale
- **[Demo Walkthrough](./docs/demo-walkthrough.md)** — Step-by-step usage guide
- **[Interview Guide](./docs/interview-guide.md)** — How to present this project

---

## 🗺 Roadmap

- [ ] LLM-based document classification (upgrade from keyword heuristics)
- [ ] Multi-language OCR support (Chinese, Japanese, Arabic)
- [ ] Batch upload and processing queue (Celery/ARQ)
- [ ] Document comparison and diff
- [ ] Fine-tuned extraction models per document type
- [ ] Authentication and multi-tenant support
- [ ] S3/GCS storage backend
- [ ] Webhook notifications on job completion
- [ ] PDF annotation and highlighting of extracted fields
- [ ] Prometheus metrics and Grafana dashboard

---

## ⚠️ Current Limitations

- **LLM Required**: Structured extraction and RAG require an OpenAI-compatible API
- **Single-threaded Pipeline**: Processing is sequential per document (horizontal scaling via multiple workers planned)
- **No Authentication**: MVP does not include auth (planned for roadmap)
- **Classifier Accuracy**: Keyword-based classification has limited accuracy vs. LLM-based
- **Local Embeddings**: `all-MiniLM-L6-v2` is good for English; multilingual model recommended for production

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.
