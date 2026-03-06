"""Export endpoints for JSON and CSV download."""

from __future__ import annotations

import csv
import io
import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from docai.core.errors import DocumentNotFoundError
from docai.database import get_db
from docai.models.document import Document, DocumentPage
from docai.models.extraction import ExtractedField

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{document_id}/json")
async def export_json(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Fetch document
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise DocumentNotFoundError(str(document_id))

    # Fetch pages
    stmt = (
        select(DocumentPage)
        .where(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number)
    )
    result = await db.execute(stmt)
    pages = result.scalars().all()

    # Fetch extracted fields
    stmt = select(ExtractedField).where(ExtractedField.document_id == document_id)
    result = await db.execute(stmt)
    fields = result.scalars().all()

    return {
        "document": {
            "id": str(doc.id),
            "filename": doc.filename,
            "document_type": doc.document_type,
            "page_count": doc.page_count,
            "status": doc.status,
        },
        "pages": [
            {
                "page_number": p.page_number,
                "text": p.text_content,
                "method": p.extraction_method,
                "confidence": p.ocr_confidence,
            }
            for p in pages
        ],
        "extracted_fields": {f.field_name: f.field_value for f in fields},
    }


@router.get("/{document_id}/csv")
async def export_csv(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    stmt = select(ExtractedField).where(ExtractedField.document_id == document_id)
    result = await db.execute(stmt)
    fields = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["field_name", "field_value", "confidence", "source_page"])
    for f in fields:
        writer.writerow([f.field_name, f.field_value, f.confidence, f.source_page])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={document_id}_extraction.csv"},
    )
