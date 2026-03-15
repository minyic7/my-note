"""Pydantic models for findings."""

from pydantic import BaseModel, Field


class FindingCreate(BaseModel):
    project_id: str
    type: str = Field(..., pattern=r"^(risk|gap|conflict|insight)$")
    content: str
    severity: str | None = Field(None, pattern=r"^(high|medium|low)$")
    source_docs: list[str]


class FindingResponse(BaseModel):
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
    status: str | None = Field(None, pattern=r"^(open|acknowledged|resolved)$")
    annotation: str | None = None
