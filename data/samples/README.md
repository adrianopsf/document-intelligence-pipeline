# Sample Documents

This directory contains synthetic sample documents for demo and testing purposes.

## Generating Samples

Run the included generator script to create ready-to-use PDF samples:

```bash
# Requires project dependencies to be installed
uv run python data/samples/generate_samples.py

# Or with plain Python (after uv sync)
python data/samples/generate_samples.py
```

This creates three PDF files:
- `sample_contract.pdf` — Contract with parties, value, dates, clauses
- `sample_invoice.pdf` — Invoice with line items, taxes, total
- `sample_financial_report.pdf` — DRE with revenue, expenses, profit

## Manual Testing

Upload via the web UI at `http://localhost:8000`, or via curl:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@data/samples/sample_contract.pdf"
```

## In Docker

The `data/samples/` directory is copied into the container at `/app/data/samples/`.
Run the generator before `docker-compose up` to have samples available immediately,
or exec into the container after startup:

```bash
docker-compose exec app python data/samples/generate_samples.py
```

