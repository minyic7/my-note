"""Pydantic models for findings."""

from pydantic import BaseModel, Field


class FindingCreate(BaseModel):
    """Request model for creating a new finding."""

    project_id: str
    type: str = Field(..., pattern=r"^(risk|gap|conflict|insight)$")
    content: str
    severity: str | None = Field(None, pattern=r"^(high|medium|low)$")
    source_docs: list[str]


class FindingResponse(BaseModel):
    """Response model for a single finding."""

    id: str
    project_id: str
    type: str
    content: str
    severity: str | None = None
    source_docs: str  # JSON string
    status: str = "open"
    annotation: str | None = None
    created_at: str
    updated_at: str


class FindingUpdate(BaseModel):
    """Request model for updating a finding's status or annotation."""

    status: str | None = Field(None, pattern=r"^(open|acknowledged|resolved)$")
    annotation: str | None = None


class FindingListResponse(BaseModel):
    """Response model for listing findings."""

    findings: list[FindingResponse]
