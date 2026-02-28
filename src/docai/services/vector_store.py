"""Qdrant vector store integration for chunk storage and semantic search."""

from __future__ import annotations

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from docai.config import settings
from docai.core.logging import get_logger
from docai.services.embedder import get_embedding_dimension

logger = get_logger(__name__)

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _client


def ensure_collection() -> None:
    client = get_qdrant()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        dim = get_embedding_dimension()
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        logger.info("qdrant_collection_created", name=settings.qdrant_collection, dim=dim)


def upsert_chunks(
    document_id: str,
    chunk_texts: list[str],
    embeddings: list[list[float]],
    page_numbers_list: list[str],
    chunk_ids: list[str],
) -> None:
    client = get_qdrant()
    ensure_collection()

    points = [
        PointStruct(
            id=cid,
            vector=emb,
            payload={
                "document_id": document_id,
                "text": text,
                "page_numbers": pages,
                "chunk_index": i,
            },
        )
        for i, (cid, emb, text, pages) in enumerate(
            zip(chunk_ids, embeddings, chunk_texts, page_numbers_list)
        )
    ]

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    logger.info("qdrant_upsert", document_id=document_id, points=len(points))


def search_similar(
    query_embedding: list[float],
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[dict]:
    client = get_qdrant()

    query_filter = None
    if document_ids:
        query_filter = Filter(
            should=[
                FieldCondition(key="document_id", match=MatchValue(value=did))
                for did in document_ids
            ]
        )

    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=top_k,
    )

    return [
        {
            "text": hit.payload.get("text", "") if hit.payload else "",
            "document_id": hit.payload.get("document_id", "") if hit.payload else "",
            "page_numbers": hit.payload.get("page_numbers", "") if hit.payload else "",
            "score": hit.score,
        }
        for hit in results
    ]


def delete_document_vectors(document_id: str) -> None:
    client = get_qdrant()
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
    )
