"""Extraction results endpoints."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from sqlalchemy import select

from docai.database import get_db
from docai.models.extraction import ExtractedField
from docai.schemas.extraction import ExtractedFieldOut, ExtractionResultOut

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.get("/{document_id}", response_model=ExtractionResultOut)
async def get_extraction(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ExtractionResultOut:
    stmt = (
        select(ExtractedField)
        .where(ExtractedField.document_id == document_id)
        .order_by(ExtractedField.field_name)
    )
    result = await db.execute(stmt)
    fields = result.scalars().all()

    return ExtractionResultOut(
        document_id=document_id,
        fields=[ExtractedFieldOut.model_validate(f) for f in fields],
        total=len(fields),
    )
