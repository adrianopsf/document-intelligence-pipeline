"""OCR service unit tests."""

from pathlib import Path

from docai.services.ocr import PyMuPDFEngine, extract_text


class TestPyMuPDFEngine:
    def test_extract_from_pdf(self, sample_pdf_path: Path) -> None:
        engine = PyMuPDFEngine()
        pages = engine.extract(sample_pdf_path)

        assert len(pages) == 1
        assert pages[0].page_number == 1
        assert pages[0].method == "native"
        assert "CONTRATO" in pages[0].text
        assert "Acme Corp" in pages[0].text

    def test_extract_preserves_page_numbers(self, sample_pdf_path: Path) -> None:
        pages = extract_text(sample_pdf_path)
        assert all(p.page_number >= 1 for p in pages)


class TestExtractText:
    def test_pdf_with_native_text(self, sample_pdf_path: Path) -> None:
        pages = extract_text(sample_pdf_path)

        assert len(pages) >= 1
        assert pages[0].text  # Should have text
        assert pages[0].method == "native"

    def test_unsupported_format(self, tmp_path: Path) -> None:
        fake = tmp_path / "test.xyz"
        fake.write_text("hello")
        pages = extract_text(fake)
        assert pages == []
