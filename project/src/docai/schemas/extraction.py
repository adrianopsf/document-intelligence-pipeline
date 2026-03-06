"""Extraction schemas for structured field output."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExtractedFieldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    field_name: str
    field_value: str | None = None
    confidence: float | None = None
    source_page: str | None = None
    created_at: datetime


class ExtractionResultOut(BaseModel):
    document_id: uuid.UUID
    fields: list[ExtractedFieldOut]
    total: int


class StructuredExtractionSchema(BaseModel):
    """Expected output schema for LLM-based extraction."""

    document_type: str | None = None
    beneficiary_name: str | None = None
    company_name: str | None = None
    issue_date: str | None = None
    due_date: str | None = None
    total_amount: str | None = None
    taxes: str | None = None
    assets: str | None = None
    obligations: str | None = None
    summary: str | None = None
