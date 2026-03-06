# Technical Decisions

## 1. OCR: PyMuPDF + Tesseract (not cloud OCR)

**Decision**: Use PyMuPDF for native text extraction with Tesseract as OCR fallback.

**Alternatives considered**: AWS Textract, Google Vision, Azure Form Recognizer

**Trade-offs**:
- ✅ Free, no API keys needed for basic operation
- ✅ Works offline, no data leaves the system (privacy)
- ✅ Strategy pattern allows easy engine swap
- ❌ Lower accuracy on complex layouts vs. cloud solutions
- ❌ Tesseract struggles with handwritten text

**Upgrade path**: Add cloud OCR engines as additional strategies.

---

## 2. Vector Store: Qdrant (not pgvector)

**Decision**: Use Qdrant as a dedicated vector database.

**Alternatives**: pgvector, Pinecone, Weaviate, ChromaDB

**Trade-offs**:
- ✅ Purpose-built for vector search (better performance at scale)
- ✅ Rich filtering capabilities (by document ID, page, etc.)
- ✅ Official Docker image, easy to deploy
- ✅ No PostgreSQL extension management
- ❌ Extra service to manage
- ❌ Not embedded like ChromaDB

---

## 3. Embeddings: sentence-transformers (local)

**Decision**: Use `all-MiniLM-L6-v2` locally.

**Alternatives**: OpenAI embeddings, Cohere, Voyage AI

**Trade-offs**:
- ✅ No API key needed, works completely offline
- ✅ Fast inference (384 dimensions, ~80MB model)
- ✅ Good balance of quality and speed
- ❌ English-optimized (multilingual model needed for production)
- ❌ Lower quality than large API-based models

---

## 4. LLM Abstraction: OpenAI-compatible API

**Decision**: Abstract LLM calls behind OpenAI client interface.

**Trade-offs**:
- ✅ Works with OpenAI, Ollama, vLLM, LiteLLM, LocalAI, etc.
- ✅ Single interface, configurable via env vars
- ✅ Easy to swap providers without code changes
- ❌ Tied to chat completions API format

---

## 5. Pipeline: synchronous stages with background tasks

**Decision**: Use FastAPI `BackgroundTasks` for async pipeline execution.

**Alternatives**: Celery, ARQ, Dramatiq, distributed task queue

**Trade-offs**:
- ✅ Simple, no extra infrastructure (no Redis/RabbitMQ)
- ✅ Sufficient for single-instance deployment
- ✅ Easy to understand and debug
- ❌ No retry mechanism for individual stages
- ❌ Not suitable for high-throughput production (needs task queue)

**Upgrade path**: Migrate to Celery/ARQ when scaling is needed.

---

## 6. Frontend: Vanilla HTML/CSS/JS

**Decision**: No framework, served as static files by FastAPI.

**Alternatives**: React, Vue, Svelte

**Trade-offs**:
- ✅ Zero build step, zero dependencies
- ✅ Reduces project complexity
- ✅ Focus stays on backend/pipeline quality
- ❌ Limited for complex UI requirements
- ❌ No component reuse patterns

---

## 7. Database: PostgreSQL + SQLAlchemy 2.0

**Decision**: Use PostgreSQL with async SQLAlchemy and Alembic.

**Trade-offs**:
- ✅ Production-standard, well-understood
- ✅ Async support with asyncpg
- ✅ Alembic for version-controlled migrations
- ✅ Rich ecosystem and tooling
- ❌ Requires running PostgreSQL service

---

## 8. Document Classification: keyword heuristics (MVP)

**Decision**: Use keyword matching for document classification.

**Trade-offs**:
- ✅ Fast, no API dependency
- ✅ Works offline
- ✅ Predictable behavior
- ❌ Limited accuracy for edge cases
- ❌ Requires manual keyword maintenance

**Upgrade path**: Replace with LLM-based or fine-tuned classifier.
