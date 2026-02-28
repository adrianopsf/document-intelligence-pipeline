"""Document request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    page_number: int
    text_content: str
    ocr_confidence: float | None = None
    extraction_method: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    filename: str
    file_size: int
    mime_type: str
    document_type: str | None = None
    status: str
    page_count: int | None = None
    created_at: datetime
    updated_at: datetime


class DocumentDetailOut(DocumentOut):
    pages: list[DocumentPageOut] = []


class DocumentListOut(BaseModel):
    documents: list[DocumentOut]
    total: int


class UploadResponse(BaseModel):
    document_id: uuid.UUID
    job_id: uuid.UUID
    filename: str
    message: str = "Document uploaded and processing started"
