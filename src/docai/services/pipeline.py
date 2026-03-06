"""Pipeline orchestrator — coordinates the full document processing pipeline.

Stages: OCR → Classify → Chunk → Embed → Extract → Complete
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select

from docai.core.errors import PipelineError
from docai.core.logging import get_logger
from docai.models.document import AuditLog, Document, DocumentPage, RagChunk
from docai.models.extraction import ExtractedField
from docai.models.job import ProcessingJob
from docai.services.chunker import chunk_pages
from docai.services.classifier import classify_document
from docai.services.embedder import embed_texts
from docai.services.extractor import extract_fields
from docai.services.ocr import extract_text
from docai.services.vector_store import upsert_chunks

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

STAGES = ["ocr", "classify", "chunk", "embed", "extract", "complete"]


async def _log_audit(
    db: AsyncSession,
    document_id: uuid.UUID,
    job_id: uuid.UUID,
    action: str,
    stage: str | None = None,
    detail: str | None = None,
) -> None:
    log = AuditLog(
        document_id=document_id,
        job_id=job_id,
        action=action,
        stage=stage,
        detail=detail,
    )
    db.add(log)
    await db.flush()


async def _update_job(
    db: AsyncSession,
    job: ProcessingJob,
    stage: str,
    progress: int,
    status: str = "processing",
) -> None:
    job.current_stage = stage
    job.progress_pct = progress
    job.status = status
    await db.flush()


async def run_pipeline(job_id: uuid.UUID, db: AsyncSession) -> None:
    """Execute the full document processing pipeline for a given job."""

    # Load the job
    stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise PipelineError("init", f"Job {job_id} not found")

    # Load the document
    stmt = select(Document).where(Document.id == job.document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise PipelineError("init", f"Document {job.document_id} not found")

    document_id = doc.id
    file_path = Path(doc.file_path)

    try:
        # Mark job as processing
        job.started_at = datetime.now(UTC)
        await _update_job(db, job, "ocr", 10)
        await _log_audit(db, document_id, job_id, "pipeline_started", "init")

        # --- Stage 1: OCR ---
        logger.info("pipeline_stage", stage="ocr", document_id=str(document_id))
        pages = extract_text(file_path)
        doc.page_count = len(pages)

        for page in pages:
            db_page = DocumentPage(
                document_id=document_id,
                page_number=page.page_number,
                text_content=page.text,
                ocr_confidence=page.confidence,
                extraction_method=page.method,
            )
            db.add(db_page)

        await db.flush()
        await _update_job(db, job, "classify", 25)
        await _log_audit(
            db, document_id, job_id, "ocr_complete", "ocr", f"Extracted {len(pages)} pages"
        )

        # --- Stage 2: Classify ---
        logger.info("pipeline_stage", stage="classify", document_id=str(document_id))
        full_text = " ".join(p.text for p in pages if p.text)
        doc_type = classify_document(full_text)
        doc.document_type = doc_type
        await _update_job(db, job, "chunk", 35)
        await _log_audit(db, document_id, job_id, "classified", "classify", f"Type: {doc_type}")

        # --- Stage 3: Chunk ---
        logger.info("pipeline_stage", stage="chunk", document_id=str(document_id))
        chunks = chunk_pages(pages)

        chunk_records: list[RagChunk] = []
        for chunk in chunks:
            chunk_id = uuid.uuid4()
            record = RagChunk(
                id=chunk_id,
                document_id=document_id,
                chunk_index=chunk.index,
                text_content=chunk.text,
                page_numbers=",".join(str(p) for p in chunk.page_numbers),
                vector_id=str(chunk_id),
            )
            db.add(record)
            chunk_records.append(record)

        await db.flush()
        await _update_job(db, job, "embed", 50)
        await _log_audit(
            db, document_id, job_id, "chunked", "chunk", f"Created {len(chunks)} chunks"
        )

        # --- Stage 4: Embed + Index ---
        logger.info("pipeline_stage", stage="embed", document_id=str(document_id))
        if chunks:
            texts = [c.text for c in chunks]
            embeddings = embed_texts(texts)

            chunk_ids_str = [str(r.id) for r in chunk_records]
            page_nums_str = [",".join(str(p) for p in c.page_numbers) for c in chunks]

            upsert_chunks(
                document_id=str(document_id),
                chunk_texts=texts,
                embeddings=embeddings,
                page_numbers_list=page_nums_str,
                chunk_ids=chunk_ids_str,
            )

        await _update_job(db, job, "extract", 70)
        await _log_audit(
            db, document_id, job_id, "embedded", "embed", f"Indexed {len(chunks)} vectors"
        )

        # --- Stage 5: Structured Extraction ---
        logger.info("pipeline_stage", stage="extract", document_id=str(document_id))
        try:
            extraction = await extract_fields(full_text, document_type=doc_type)
            for field_name, field_value in extraction.model_dump().items():
                if field_value is not None:
                    db.add(
                        ExtractedField(
                            document_id=document_id,
                            field_name=field_name,
                            field_value=str(field_value),
                        )
                    )
            await db.flush()
            await _log_audit(db, document_id, job_id, "extracted", "extract")
        except Exception as e:
            logger.warning("extraction_skipped", error=str(e))
            await _log_audit(db, document_id, job_id, "extraction_skipped", "extract", str(e))

        # --- Complete ---
        doc.status = "processed"
        job.status = "completed"
        job.progress_pct = 100
        job.current_stage = "complete"
        job.completed_at = datetime.now(UTC)
        await _log_audit(db, document_id, job_id, "pipeline_complete", "complete")

        await db.commit()
        logger.info("pipeline_complete", document_id=str(document_id), job_id=str(job_id))

    except Exception as e:
        logger.error("pipeline_failed", error=str(e), document_id=str(document_id))
        job.status = "failed"
        job.error_message = str(e)
        doc.status = "failed"
        await _log_audit(db, document_id, job_id, "pipeline_failed", job.current_stage, str(e))
        await db.commit()
        raise PipelineError(job.current_stage or "unknown", str(e)) from e
