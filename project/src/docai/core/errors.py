"""Centralized error handling for the API."""

from fastapi import HTTPException, status


class DocumentNotFoundError(HTTPException):
    def __init__(self, document_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )


class JobNotFoundError(HTTPException):
    def __init__(self, job_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing job not found: {job_id}",
        )


class UploadError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload error: {detail}",
        )


class PipelineError(Exception):
    def __init__(self, stage: str, detail: str) -> None:
        self.stage = stage
        self.detail = detail
        super().__init__(f"Pipeline failed at {stage}: {detail}")


class LLMError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"LLM error: {detail}")
