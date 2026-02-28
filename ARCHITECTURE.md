# Architecture

## System Overview

The Document Intelligence Pipeline follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│            Frontend (Static SPA)        │  ← Vanilla HTML/CSS/JS
├─────────────────────────────────────────┤
│            API Layer (FastAPI)          │  ← Request/response handling
├─────────────────────────────────────────┤
│            Service Layer               │  ← Business logic
├───────┬───────┬───────┬───────┬────────┤
│  OCR  │Classify│Chunk │ Embed │Extract │  ← Domain services
├───────┴───────┴───────┴───────┴────────┤
│         Pipeline Orchestrator          │  ← Coordination + state
├──────────────────┬─────────────────────┤
│   PostgreSQL     │      Qdrant         │  ← Persistence
└──────────────────┴─────────────────────┘
```

## Data Flow

### Document Ingestion Pipeline

```
1. UPLOAD    → File saved to disk, Document record created
2. OCR       → PyMuPDF extracts native text; Tesseract fallback for scanned pages
3. CLASSIFY  → Keyword-based document type detection
4. CHUNK     → Text split into overlapping chunks with page references
5. EMBED     → sentence-transformers generates vectors for each chunk
6. INDEX     → Vectors stored in Qdrant with metadata payload
7. EXTRACT   → LLM extracts structured fields (JSON schema validated)
8. COMPLETE  → Job marked complete, document status updated
```

### RAG Query Flow

```
1. User submits question
2. Question embedded using same model
3. Qdrant returns top-k similar chunks (optionally filtered by document)
4. Context assembled with page references
5. LLM generates grounded answer with citations
6. Response includes answer + source chunks
```

## Database Schema

| Table | Purpose |
|-------|---------|
| `documents` | File metadata, type, status |
| `document_pages` | Per-page text, OCR confidence, extraction method |
| `processing_jobs` | Job state machine (pending → processing → completed/failed) |
| `extracted_fields` | Key-value extraction results per document |
| `rag_chunks` | Text chunks with page refs and vector IDs |
| `audit_logs` | Pipeline event log for traceability |

## Design Patterns

- **Strategy Pattern**: OCR engines (PyMuPDF, Tesseract) are interchangeable
- **Pipeline Pattern**: Sequential stages with state tracking
- **Repository Pattern**: SQLAlchemy models isolate data access
- **Provider Abstraction**: LLM client works with any OpenAI-compatible API
- **Background Tasks**: FastAPI BackgroundTasks for async pipeline execution

## Technology Rationale

See [Technical Decisions](./docs/decisions.md) for detailed trade-off analysis.
