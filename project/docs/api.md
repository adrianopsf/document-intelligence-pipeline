# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger) | `http://localhost:8000/redoc` (ReDoc)

---

## Health

### `GET /health`

```json
{ "status": "healthy", "app": "Document Intelligence Pipeline", "version": "0.1.0" }
```

---

## Documents

### `POST /documents/upload`

Upload a document for processing. Automatically triggers the pipeline.

**Request**: `multipart/form-data` with `file` field  
**Accepted**: PDF, PNG, JPG, TIFF, BMP (max 50MB)

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@document.pdf"
```

**Response** (201):
```json
{
  "document_id": "uuid",
  "job_id": "uuid",
  "filename": "document.pdf",
  "message": "Document uploaded and processing started"
}
```

### `GET /documents`

List all documents with pagination.

**Query**: `skip` (default 0), `limit` (default 50)

```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "contract.pdf",
      "file_size": 102400,
      "mime_type": "application/pdf",
      "document_type": "contract",
      "status": "processed",
      "page_count": 3,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:01:30Z"
    }
  ],
  "total": 1
}
```

### `GET /documents/{id}`

Get document detail including extracted page text.

---

## Jobs

### `GET /jobs/{id}`

```json
{
  "id": "uuid",
  "document_id": "uuid",
  "status": "completed",
  "current_stage": "complete",
  "progress_pct": 100,
  "error_message": null,
  "started_at": "2024-01-15T10:00:01Z",
  "completed_at": "2024-01-15T10:01:30Z"
}
```

### `GET /jobs?document_id={id}`

List jobs, optionally filtered by document.

---

## Extraction

### `GET /extraction/{document_id}`

```json
{
  "document_id": "uuid",
  "fields": [
    { "field_name": "company_name", "field_value": "Acme Corp", "confidence": null },
    { "field_name": "total_amount", "field_value": "R$ 15.000,00", "confidence": null }
  ],
  "total": 10
}
```

---

## RAG

### `POST /rag/query`

**Request**:
```json
{
  "question": "What is the total contract value?",
  "document_ids": ["uuid"],
  "top_k": 5
}
```

**Response**:
```json
{
  "answer": "The total contract value is R$ 15.000,00 (page 1).",
  "sources": [
    {
      "chunk_text": "Valor Total: R$ 15.000,00...",
      "page_numbers": "1",
      "document_id": "uuid",
      "document_name": "contract.pdf",
      "score": 0.892
    }
  ],
  "question": "What is the total contract value?"
}
```

---

## Export

### `GET /export/{document_id}/json`

Full document export with pages and extracted fields.

### `GET /export/{document_id}/csv`

Extracted fields as downloadable CSV.
