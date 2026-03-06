"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from docai.api.documents import router as documents_router
from docai.api.export import router as export_router
from docai.api.extraction import router as extraction_router
from docai.api.health import router as health_router
from docai.api.jobs import router as jobs_router
from docai.api.rag import router as rag_router
from docai.config import settings
from docai.core.errors import PipelineError
from docai.core.logging import get_logger, setup_logging
from docai.database import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger.info("app_starting", version=settings.app_version)
    await init_db()
    logger.info("database_initialized")
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade Document Intelligence Pipeline"
        " with OCR, RAG, and structured extraction."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
API_PREFIX = "/api/v1"
app.include_router(health_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(jobs_router, prefix=API_PREFIX)
app.include_router(extraction_router, prefix=API_PREFIX)
app.include_router(rag_router, prefix=API_PREFIX)
app.include_router(export_router, prefix=API_PREFIX)

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.exception_handler(PipelineError)
async def pipeline_error_handler(request: Request, exc: PipelineError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "pipeline_error",
            "stage": exc.stage,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred."},
    )
