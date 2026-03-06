"""Structured field extraction using LLM with JSON schema validation."""

from __future__ import annotations

import json

from docai.core.llm import llm_json_completion
from docai.core.logging import get_logger
from docai.schemas.extraction import StructuredExtractionSchema

logger = get_logger(__name__)

EXTRACTION_PROMPT = """Analyze the following document text and extract structured information.

Return a JSON object with these fields (use null if not found):
- document_type: type of document (contract, invoice, financial_report, legal, receipt, other)
- beneficiary_name: name of the beneficiary or recipient
- company_name: company or organization name
- issue_date: date of issuance (ISO format YYYY-MM-DD if possible)
- due_date: due date or expiration date (ISO format if possible)
- total_amount: total monetary amount (as string with currency)
- taxes: tax amounts mentioned
- assets: assets mentioned
- obligations: obligations or liabilities mentioned
- summary: brief 2-3 sentence summary of the document

DOCUMENT TEXT:
{text}

Respond ONLY with the JSON object, no additional text."""


async def extract_fields(text: str, document_type: str | None = None) -> StructuredExtractionSchema:
    """Extract structured fields from document text using LLM.

    Returns validated StructuredExtractionSchema.
    """
    if not text.strip():
        return StructuredExtractionSchema()

    # Truncate very long texts to stay within token limits
    truncated = text[:8000] if len(text) > 8000 else text
    prompt = EXTRACTION_PROMPT.format(text=truncated)

    raw = ""
    try:
        raw = await llm_json_completion(prompt)
        data = json.loads(raw)

        # Override with classifier result if we have one
        if document_type and not data.get("document_type"):
            data["document_type"] = document_type

        result = StructuredExtractionSchema(**data)
        logger.info("extraction_complete", fields_found=sum(1 for v in data.values() if v))
        return result

    except json.JSONDecodeError:
        logger.error("extraction_json_parse_error", raw_length=len(raw))
        return StructuredExtractionSchema(document_type=document_type)
    except Exception as e:
        logger.error("extraction_error", error=str(e))
        return StructuredExtractionSchema(document_type=document_type)
