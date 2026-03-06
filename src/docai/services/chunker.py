"""Configurable text chunking with page reference preservation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from docai.core.logging import get_logger

if TYPE_CHECKING:
    from docai.services.ocr import PageText

logger = get_logger(__name__)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64


@dataclass
class TextChunk:
    index: int
    text: str
    page_numbers: list[int]


def chunk_pages(
    pages: list[PageText],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    """Split page texts into overlapping chunks, preserving page references.

    Uses sentence-boundary-aware splitting: tries to break at sentence endings
    within the chunk window. Each chunk tracks which pages contributed to it.
    """
    if not pages:
        return []

    # Build a list of (char_start, char_end, page_number) for page tracking
    segments: list[tuple[int, int, int]] = []
    full_text_parts: list[str] = []
    offset = 0
    for page in pages:
        text = page.text.strip()
        if not text:
            continue
        start = offset
        full_text_parts.append(text)
        offset += len(text) + 1  # +1 for the separator
        segments.append((start, offset - 1, page.page_number))

    full_text = " ".join(full_text_parts)
    if not full_text.strip():
        return []

    chunks: list[TextChunk] = []
    pos = 0
    idx = 0

    while pos < len(full_text):
        end = min(pos + chunk_size, len(full_text))
        chunk_text = full_text[pos:end]

        # Try to break at sentence boundary
        if end < len(full_text):
            last_period = chunk_text.rfind(". ")
            last_newline = chunk_text.rfind("\n")
            break_at = max(last_period, last_newline)
            if break_at > chunk_size // 3:
                chunk_text = chunk_text[: break_at + 1].strip()
                end = pos + break_at + 1

        if not chunk_text.strip():
            pos = end
            continue

        # Determine which pages this chunk spans
        chunk_pages_set: set[int] = set()
        chunk_start = pos
        chunk_end = pos + len(chunk_text)
        for seg_start, seg_end, page_num in segments:
            if seg_start < chunk_end and seg_end > chunk_start:
                chunk_pages_set.add(page_num)

        chunks.append(
            TextChunk(
                index=idx,
                text=chunk_text.strip(),
                page_numbers=sorted(chunk_pages_set),
            )
        )
        idx += 1

        # Advance with overlap
        pos = max(pos + 1, end - overlap)

    logger.info("chunking_complete", total_chunks=len(chunks), chunk_size=chunk_size)
    return chunks
