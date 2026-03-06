# Demo Walkthrough

This guide walks through the full pipeline from upload to Q&A.

## 1. Start the Application

```bash
docker-compose up --build -d
# Open http://localhost:8000
```

## 2. Upload a Document

### Via UI
1. Open `http://localhost:8000`
2. Drag & drop a PDF into the upload zone
3. Watch the job progress bar update in real-time

### Via API
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@my_contract.pdf"
```

**Response:**
```json
{
  "document_id": "a1b2c3d4-...",
  "job_id": "e5f6g7h8-...",
  "filename": "my_contract.pdf",
  "message": "Document uploaded and processing started"
}
```

## 3. Check Processing Status

```bash
curl http://localhost:8000/api/v1/jobs/e5f6g7h8-...
```

The job progresses through stages: `ocr → classify → chunk → embed → extract → complete`

## 4. View Extracted Data

### Extracted Text (per page)
```bash
curl http://localhost:8000/api/v1/documents/a1b2c3d4-...
```

### Structured Fields
```bash
curl http://localhost:8000/api/v1/extraction/a1b2c3d4-...
```

Example output:
```json
{
  "fields": [
    { "field_name": "company_name", "field_value": "Acme Corp Ltda." },
    { "field_name": "beneficiary_name", "field_value": "João da Silva" },
    { "field_name": "total_amount", "field_value": "R$ 15.000,00" },
    { "field_name": "issue_date", "field_value": "2024-01-15" },
    { "field_name": "document_type", "field_value": "contract" }
  ]
}
```

## 5. Ask Questions (RAG)

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual o valor total do contrato?"}'
```

**Response:**
```json
{
  "answer": "O valor total do contrato é R$ 15.000,00, conforme indicado na página 1 do documento.",
  "sources": [
    {
      "chunk_text": "Valor Total: R$ 15.000,00...",
      "page_numbers": "1",
      "document_name": "my_contract.pdf",
      "score": 0.89
    }
  ]
}
```

## 6. Export Results

```bash
# JSON
curl http://localhost:8000/api/v1/export/a1b2c3d4-.../json

# CSV
curl -o extraction.csv http://localhost:8000/api/v1/export/a1b2c3d4-.../csv
```

## Example Payloads

### Upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload -F "file=@invoice.pdf"
```

### RAG with specific documents
```json
{
  "question": "What are the payment terms?",
  "document_ids": ["doc-uuid-1", "doc-uuid-2"],
  "top_k": 5
}
```

### List documents with pagination
```bash
curl "http://localhost:8000/api/v1/documents?skip=0&limit=10"
```
