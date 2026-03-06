"""OCR service with pluggable engine architecture.

Supports strategy pattern for engine swapping:
- PyMuPDFEngine: extracts native text from PDFs (fast, no OCR)
- TesseractEngine: OCR for scanned documents/images
- Auto-fallback: tries native extraction first, falls back to OCR if empty
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from docai.config import settings
from docai.core.logging import get_logger

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger(__name__)

if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


@dataclass
class PageText:
    page_number: int
    text: str
    method: str  # "native" or "ocr"
    confidence: float | None = None


class OCREngine(abc.ABC):
    @abc.abstractmethod
    def extract(self, file_path: Path) -> list[PageText]:
        ...


class PyMuPDFEngine(OCREngine):
    """Extract text from PDFs using PyMuPDF (native text extraction)."""

    def extract(self, file_path: Path) -> list[PageText]:
        pages: list[PageText] = []
        doc = fitz.open(str(file_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            pages.append(PageText(
                page_number=page_num + 1,
                text=text,
                method="native",
            ))
        doc.close()
        return pages


class TesseractEngine(OCREngine):
    """OCR engine using Tesseract for scanned documents and images."""

    def extract(self, file_path: Path) -> list[PageText]:
        pages: list[PageText] = []
        suffix = file_path.suffix.lower()

        if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"):
            img = Image.open(file_path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            text = " ".join(w for w in data["text"] if w.strip())
            confs = [int(c) for c in data["conf"] if int(c) > 0]
            avg_conf = sum(confs) / len(confs) if confs else 0.0
            pages.append(PageText(
                page_number=1,
                text=text,
                method="ocr",
                confidence=avg_conf / 100.0,
            ))
        elif suffix == ".pdf":
            doc = fitz.open(str(file_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                text = " ".join(w for w in data["text"] if w.strip())
                confs = [int(c) for c in data["conf"] if int(c) > 0]
                avg_conf = sum(confs) / len(confs) if confs else 0.0
                pages.append(PageText(
                    page_number=page_num + 1,
                    text=text,
                    method="ocr",
                    confidence=avg_conf / 100.0,
                ))
            doc.close()

        return pages


def extract_text(file_path: Path) -> list[PageText]:
    """Extract text with automatic fallback: native → OCR.

    For PDFs: tries native extraction first. If a page has no text, uses OCR.
    For images: uses OCR directly.
    """
    suffix = file_path.suffix.lower()

    if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"):
        logger.info("ocr_extract", file=str(file_path), engine="tesseract")
        return TesseractEngine().extract(file_path)

    if suffix != ".pdf":
        logger.warning("unsupported_format", file=str(file_path), suffix=suffix)
        return []

    native = PyMuPDFEngine()
    pages = native.extract(file_path)

    empty_pages = [p for p in pages if not p.text]
    if empty_pages:
        logger.info(
            "ocr_fallback",
            file=str(file_path),
            empty_pages=len(empty_pages),
            total_pages=len(pages),
        )
        ocr = TesseractEngine()
        ocr_pages = ocr.extract(file_path)
        ocr_map = {p.page_number: p for p in ocr_pages}

        for page in pages:
            if not page.text and page.page_number in ocr_map:
                ocr_page = ocr_map[page.page_number]
                page.text = ocr_page.text
                page.method = "ocr"
                page.confidence = ocr_page.confidence

    logger.info(
        "extraction_complete",
        file=str(file_path),
        pages=len(pages),
        has_text=sum(1 for p in pages if p.text),
    )
    return pages
