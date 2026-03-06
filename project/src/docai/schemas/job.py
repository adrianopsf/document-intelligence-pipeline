"""Job request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    document_id: uuid.UUID
    status: str
    current_stage: str | None = None
    progress_pct: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class JobCreateRequest(BaseModel):
    document_id: uuid.UUID
