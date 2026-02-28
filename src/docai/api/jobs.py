"""Job status and management endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from docai.core.errors import JobNotFoundError
from docai.database import get_db
from docai.models.job import ProcessingJob
from docai.schemas.job import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JobOut:
    stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise JobNotFoundError(str(job_id))
    return JobOut.model_validate(job)


@router.get("", response_model=list[JobOut])
async def list_jobs(
    document_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[JobOut]:
    stmt = select(ProcessingJob).order_by(ProcessingJob.created_at.desc())
    if document_id:
        stmt = stmt.where(ProcessingJob.document_id == document_id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return [JobOut.model_validate(j) for j in jobs]
