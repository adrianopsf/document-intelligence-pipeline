# Interview Guide — Document Intelligence Pipeline

## Elevator Pitch (30 seconds)

> "I built a production-grade Document Intelligence Pipeline that processes business documents using OCR, classifies them, extracts structured fields with LLMs, and enables Q&A through RAG. It handles contracts, invoices, and financial reports with a pluggable OCR engine, vector search for semantic retrieval, and full pipeline traceability. Everything runs in Docker with PostgreSQL and Qdrant."

---

## Key Talking Points

### 1. Architecture & Design Decisions

- **Layered architecture**: API → Services → Data, with clear separation of concerns
- **Strategy pattern for OCR**: PyMuPDF for native PDF text, Tesseract for scanned docs, with automatic fallback
- **Provider abstraction for LLM**: Works with OpenAI, Ollama, vLLM — configurable via env vars
- **Pipeline orchestrator**: Sequential stages with state tracking, audit logging, and error recovery

### 2. AI/ML Engineering Skills Demonstrated

- **OCR pipeline** with page-level tracking and confidence scoring
- **Embedding generation** using sentence-transformers with normalized vectors
- **Vector indexing** with Qdrant for semantic search
- **RAG implementation** with grounded answers and source citations
- **Structured extraction** using LLM with JSON schema validation
- **Prompt engineering** for extraction and Q&A tasks

### 3. Backend Engineering

- **FastAPI** with async/await throughout
- **SQLAlchemy 2.0** with async session management
- **Alembic** for database migrations
- **Background task processing** for non-blocking pipeline execution
- **Centralized error handling** with domain-specific exceptions
- **Structured logging** with structlog (JSON format)

### 4. Infrastructure & DevOps

- **Docker multi-service** setup (app + PostgreSQL + Qdrant)
- **Health checks** for all services
- **GitHub Actions CI** with lint, test, and Docker build
- **Environment-based configuration** with pydantic-settings

---

## Common Interview Questions

### "Why this project?"
> "Document AI is one of the highest-impact applications of LLMs in enterprise. This project demonstrates end-to-end ML engineering — from raw document ingestion to structured output and natural language queries. It's the kind of system that saves thousands of hours of manual document review."

### "Why Qdrant over pgvector?"
> "While pgvector works for simple cases, Qdrant is purpose-built for vector search with better filtering, more distance metrics, and horizontal scaling. In production, you'd want the vector workload isolated from your transactional database."

### "How would you scale this?"
> "Three main vectors: (1) Replace BackgroundTasks with Celery/ARQ for distributed workers, (2) Add horizontal app instances behind a load balancer, (3) Use S3 for document storage. Qdrant already supports clustering."

### "What would you do differently in production?"
> "Add authentication (JWT/OAuth), rate limiting, S3 storage, async task queue with retry, monitoring (Prometheus + Grafana), and upgrade to a multilingual embedding model. I'd also fine-tune extraction prompts per document type."

### "How does the RAG work?"
> "When a user asks a question, I embed it with the same model used for document chunks, search Qdrant for the top-k most similar chunks, assemble them as context with page references, and prompt the LLM to generate a grounded answer. The response includes citations back to specific pages."

---

## Skills Proven By This Project

| Skill | Evidence |
|-------|----------|
| AI/ML Engineering | OCR pipeline, embeddings, RAG, LLM integration |
| Document AI | Multi-format processing, structured extraction |
| Backend Engineering | FastAPI, async Python, database design |
| Data Modeling | PostgreSQL schema, vector store design |
| DevOps | Docker Compose, CI/CD, environment management |
| Software Design | Strategy pattern, layered architecture, error handling |
| Production Readiness | Logging, health checks, configuration management |
