# Sample Documents

This directory contains synthetic sample documents for demo and testing purposes.

To add sample documents for testing:
1. Place PDF or image files in this directory
2. They will be available inside Docker containers at `/app/data/samples/`

## Creating Synthetic Test Documents

The test suite generates synthetic PDFs automatically via PyMuPDF.
See `tests/conftest.py` for the `sample_pdf_path` fixture.

## Manual Testing

Upload sample documents via the API:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@data/samples/your_document.pdf"
```
