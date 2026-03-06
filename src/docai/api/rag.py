"""RAG Q&A endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from docai.database import get_db
from docai.schemas.rag import RagQueryRequest, RagQueryResponse
from docai.services.rag import query_documents

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(
    request: RagQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> RagQueryResponse:
    return await query_documents(
        question=request.question,
        db=db,
        document_ids=request.document_ids,
        top_k=request.top_k,
    )
