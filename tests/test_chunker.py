"""Chunker unit tests."""

from docai.services.chunker import TextChunk, chunk_pages
from docai.services.ocr import PageText


class TestChunker:
    def test_empty_input(self) -> None:
        assert chunk_pages([]) == []

    def test_single_page_chunking(self) -> None:
        pages = [
            PageText(page_number=1, text="Hello world. This is a test document.", method="native")
        ]
        chunks = chunk_pages(pages, chunk_size=20, overlap=5)

        assert len(chunks) >= 1
        assert all(isinstance(c, TextChunk) for c in chunks)
        assert all(1 in c.page_numbers for c in chunks)

    def test_page_reference_tracking(self) -> None:
        pages = [
            PageText(page_number=1, text="First page content here.", method="native"),
            PageText(page_number=2, text="Second page content here.", method="native"),
        ]
        chunks = chunk_pages(pages, chunk_size=1000, overlap=0)

        # With large chunk size, all text fits in one chunk spanning both pages
        assert len(chunks) >= 1
        combined_pages = set()
        for c in chunks:
            combined_pages.update(c.page_numbers)
        assert 1 in combined_pages
        assert 2 in combined_pages

    def test_empty_pages_skipped(self) -> None:
        pages = [
            PageText(page_number=1, text="", method="native"),
            PageText(page_number=2, text="Content here.", method="native"),
        ]
        chunks = chunk_pages(pages, chunk_size=100, overlap=0)
        assert len(chunks) >= 1
        assert chunks[0].text.strip() != ""

    def test_chunk_indices_sequential(self) -> None:
        pages = [PageText(page_number=1, text="A " * 500, method="native")]
        chunks = chunk_pages(pages, chunk_size=100, overlap=10)
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))


class TestClassifier:
    def test_contract_classification(self) -> None:
        from docai.services.classifier import classify_document

        assert classify_document("contrato cláusula vigência partes") == "contract"

    def test_invoice_classification(self) -> None:
        from docai.services.classifier import classify_document

        assert classify_document("nota fiscal valor total quantidade") == "invoice"

    def test_unknown_classification(self) -> None:
        from docai.services.classifier import classify_document

        assert classify_document("xyzzy random gibberish") == "other"
