"""RAG request/response schemas."""

import uuid

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    document_ids: list[uuid.UUID] | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    chunk_text: str
    page_numbers: str
    document_id: uuid.UUID
    document_name: str
    score: float


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    question: str
