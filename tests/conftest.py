"""Test configuration and fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio

# Override settings before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///./test.db"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"
os.environ["LLM_API_KEY"] = "test-key"
os.environ["UPLOAD_DIR"] = "./data/test_uploads"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_db() -> AsyncGenerator[None, None]:
    from docai.database import init_db
    await init_db()
    yield


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """Create a minimal synthetic PDF for testing."""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 100),
        "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\n"
        "Empresa: Acme Corp Ltda.\n"
        "Beneficiário: João da Silva\n"
        "Data de Emissão: 2024-01-15\n"
        "Valor Total: R$ 15.000,00\n\n"
        "Cláusula 1: O contratante compromete-se a prestar serviços conforme especificado.\n"
        "Cláusula 2: O pagamento será efetuado em 30 dias após a emissão da nota fiscal.\n"
        "Cláusula 3: Vigência de 12 meses a partir da assinatura.\n",
        fontsize=11,
    )
    pdf_path = tmp_path / "sample_contract.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def sample_text() -> str:
    return (
        "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\n"
        "Empresa: Acme Corp Ltda.\n"
        "Beneficiário: João da Silva\n"
        "Data de Emissão: 2024-01-15\n"
        "Valor Total: R$ 15.000,00\n\n"
        "Cláusula 1: O contratante compromete-se.\n"
    )
