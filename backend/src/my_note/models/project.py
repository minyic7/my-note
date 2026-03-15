"""Pydantic models for projects."""

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    created_at: str
