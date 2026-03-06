"""API endpoint integration tests using FastAPI TestClient."""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_ok(self) -> None:
        from docai.main import app

        with TestClient(app) as client:
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        # Status is "healthy" when all deps ok, or "degraded" in test environment
        assert data["status"] in ("healthy", "degraded")
        assert "version" in data
        assert "checks" in data


class TestDocumentEndpoints:
    def test_list_documents_empty(self) -> None:
        from docai.main import app

        with TestClient(app) as client:
            response = client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data

    def test_get_nonexistent_document(self) -> None:
        from docai.main import app

        with TestClient(app) as client:
            response = client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404


class TestJobEndpoints:
    def test_get_nonexistent_job(self) -> None:
        from docai.main import app

        with TestClient(app) as client:
            response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404


class TestRagEndpoint:
    def test_rag_query_validation(self) -> None:
        from docai.main import app

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/rag/query",
                json={"question": "ab"},  # Too short
            )

        assert response.status_code == 422  # Validation error
