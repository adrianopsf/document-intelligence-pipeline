"""Application configuration using pydantic-settings."""

from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Document Intelligence Pipeline"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://docai:docai_secret@localhost:5432/docai"
    database_url_sync: str = "postgresql://docai:docai_secret@localhost:5432/docai"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "docai_chunks"

    # LLM
    llm_api_key: str = "sk-placeholder"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # OCR
    tesseract_cmd: str | None = None

    # Upload
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50

    # CORS
    cors_origins: list[str] = ["http://localhost:8000", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
