"""Health check endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from sqlalchemy import text

from docai.config import settings
from docai.database import get_db

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck(db: AsyncSession = Depends(get_db)) -> dict:
    checks: dict[str, str] = {}

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:
        checks["postgres"] = f"error: {exc}"

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=3)
        client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as exc:
        checks["qdrant"] = f"error: {exc}"

    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "app": settings.app_name,
        "version": settings.app_version,
        "checks": checks,
    }
