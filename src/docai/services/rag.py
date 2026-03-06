"""RAG (Retrieval-Augmented Generation) service for document Q&A.

Handles query processing, semantic search, context assembly, and grounded answer generation.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

from docai.core.llm import llm_completion
from docai.core.logging import get_logger
from docai.models.document import Document
from docai.schemas.rag import RagQueryResponse, SourceChunk
from docai.services.embedder import embed_query
from docai.services.vector_store import search_similar

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

RAG_SYSTEM_PROMPT = (
    "You are a document analysis assistant. "
    "Answer questions based ONLY on the provided context chunks.\n\n"
    "Rules:\n"
    "1. Only use information from the provided context\n"
    '2. If the answer is not in the context, say "I could not find this information'
    ' in the provided documents."\n'
    "3. Cite your sources by referencing page numbers when available\n"
    "4. Be precise and factual\n"
    "5. If the question is in Portuguese, answer in Portuguese. "
    "If in English, answer in English."
)

RAG_PROMPT = """Based on the following document excerpts, answer the question.

CONTEXT:
{context}

QUESTION: {question}

Provide a clear, well-structured answer with citations to page numbers where applicable."""


async def query_documents(
    question: str,
    db: AsyncSession,
    document_ids: list[uuid.UUID] | None = None,
    top_k: int = 5,
) -> RagQueryResponse:
    """Run RAG query: embed question → retrieve chunks → generate answer."""

    # 1. Embed the question
    query_emb = embed_query(question)

    # 2. Search for similar chunks
    doc_id_strs = [str(did) for did in document_ids] if document_ids else None
    results = search_similar(query_emb, top_k=top_k, document_ids=doc_id_strs)

    if not results:
        return RagQueryResponse(
            answer="No relevant document chunks found for your question.",
            sources=[],
            question=question,
        )

    # 3. Fetch document names for citations
    doc_ids_found = list({r["document_id"] for r in results})
    doc_names: dict[str, str] = {}
    for did in doc_ids_found:
        try:
            doc_uuid = uuid.UUID(did)
            stmt = select(Document).where(Document.id == doc_uuid)
            result = await db.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc_names[did] = doc.filename
        except (ValueError, Exception):
            doc_names[did] = "Unknown"

    # 4. Build context
    context_parts: list[str] = []
    sources: list[SourceChunk] = []
    for i, chunk in enumerate(results):
        doc_name = doc_names.get(chunk["document_id"], "Unknown")
        page_info = f" (pages: {chunk['page_numbers']})" if chunk["page_numbers"] else ""
        context_parts.append(f"[Source {i + 1} - {doc_name}{page_info}]\n{chunk['text']}")
        sources.append(
            SourceChunk(
                chunk_text=chunk["text"][:500],
                page_numbers=chunk["page_numbers"],
                document_id=uuid.UUID(chunk["document_id"]),
                document_name=doc_name,
                score=chunk["score"],
            )
        )

    context = "\n\n---\n\n".join(context_parts)

    # 5. Generate grounded answer
    prompt = RAG_PROMPT.format(context=context, question=question)
    answer = await llm_completion(prompt, system_prompt=RAG_SYSTEM_PROMPT)

    logger.info("rag_query_complete", question_len=len(question), sources=len(sources))

    return RagQueryResponse(
        answer=answer,
        sources=sources,
        question=question,
    )
