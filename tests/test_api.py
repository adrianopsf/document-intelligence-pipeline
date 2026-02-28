"""API endpoint integration tests using FastAPI TestClient."""

import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self) -> None:
        # Lazy import to pick up env overrides
        from docai.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestDocumentEndpoints:
    @pytest.mark.asyncio
    async def test_list_documents_empty(self) -> None:
        from docai.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self) -> None:
        from docai.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/documents/00000000-0000-0000-0000-000000000000"
            )

        assert response.status_code == 404


class TestJobEndpoints:
    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self) -> None:
        from docai.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/jobs/00000000-0000-0000-0000-000000000000"
            )

        assert response.status_code == 404


class TestRagEndpoint:
    @pytest.mark.asyncio
    async def test_rag_query_validation(self) -> None:
        from docai.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/rag/query",
                json={"question": "ab"},  # Too short
            )

        assert response.status_code == 422  # Validation error
