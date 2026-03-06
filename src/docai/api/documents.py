"""Document upload and listing endpoints."""

from __future__ import annotations

import asyncio
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from docai.config import settings
from docai.core.errors import DocumentNotFoundError, UploadError
from docai.core.logging import get_logger
from docai.database import async_session, get_db
from docai.models.document import Document
from docai.models.job import ProcessingJob
from docai.schemas.document import (
    DocumentDetailOut,
    DocumentListOut,
    DocumentOut,
    UploadResponse,
)
from docai.services.pipeline import run_pipeline

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp",
}


async def _run_pipeline_bg(job_id: uuid.UUID) -> None:
    """Background task: runs the full pipeline in its own DB session."""
    async with async_session() as session:
        try:
            await run_pipeline(job_id, session)
        except Exception as exc:
            logger.error("background_pipeline_failed", job_id=str(job_id), error=str(exc))


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    if not file.filename:
        raise UploadError("No filename provided")

    # Sanitize filename — strip any path components to prevent path traversal
    safe_filename = Path(file.filename).name
    if not safe_filename:
        raise UploadError("Invalid filename")

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise UploadError(f"Unsupported file type: {content_type}. Allowed: {', '.join(ALLOWED_TYPES)}")

    # Read and validate size
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise UploadError(f"File too large. Max: {settings.max_upload_size_mb}MB")

    # Save file
    doc_id = uuid.uuid4()
    save_dir = settings.upload_path / str(doc_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / safe_filename
    file_path.write_bytes(content)

    # Create document record
    doc = Document(
        id=doc_id,
        filename=safe_filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=content_type,
        status="uploaded",
    )
    db.add(doc)

    # Create processing job
    job = ProcessingJob(document_id=doc_id, status="pending")
    db.add(job)
    await db.flush()

    job_id = job.id

    # Run pipeline in background
    background_tasks.add_task(_run_pipeline_bg, job_id)

    return UploadResponse(
        document_id=doc_id,
        job_id=job_id,
        filename=file.filename,
    )


@router.get("", response_model=DocumentListOut)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> DocumentListOut:
    count_stmt = select(func.count()).select_from(Document)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    docs = result.scalars().all()

    return DocumentListOut(
        documents=[DocumentOut.model_validate(d) for d in docs],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentDetailOut)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetailOut:
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise DocumentNotFoundError(str(document_id))
    return DocumentDetailOut.model_validate(doc)
