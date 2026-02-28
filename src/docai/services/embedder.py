"""Embedding service using sentence-transformers (local, no API key needed)."""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from docai.config import settings
from docai.core.logging import get_logger

logger = get_logger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("loading_embedding_model", model=settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if not texts:
        return []
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return [e.tolist() for e in embeddings]


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    model = get_model()
    embedding = model.encode([query], show_progress_bar=False, normalize_embeddings=True)
    return embedding[0].tolist()


def get_embedding_dimension() -> int:
    model = get_model()
    return model.get_sentence_embedding_dimension() or 384
