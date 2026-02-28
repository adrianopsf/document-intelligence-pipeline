"""Health check endpoint."""

from fastapi import APIRouter

from docai.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict:
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
