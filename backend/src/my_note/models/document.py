"""Pydantic models for documents."""

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Request model for creating a new document."""

    project_id: str
    title: str | None = None
    source_type: str = Field(..., pattern=r"^(pdf|url|code|text|docx)$")
    source_path: str | None = None
    source_url: str | None = None


class DocumentResponse(BaseModel):
    """Response model for a single document."""

    id: str
    project_id: str
    title: str | None = None
    source_type: str
    source_path: str | None = None
    source_url: str | None = None
    ingested_at: str
    chunk_count: int = 0
    analysis_done: int = 0
    error_message: str | None = None


class DocumentStatusUpdate(BaseModel):
    """Request model for updating document analysis status."""

    analysis_done: int = Field(..., ge=0, le=2)
    error_message: str | None = None
    chunk_count: int | None = None


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""

    documents: list[DocumentResponse]
