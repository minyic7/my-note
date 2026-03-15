"""Pydantic models for projects."""

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Request model for creating a new project."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class ProjectUpdate(BaseModel):
    """Request model for updating project fields."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


class ProjectResponse(BaseModel):
    """Response model for a single project."""

    id: str
    name: str
    description: str | None = None
    created_at: str


class ProjectListResponse(BaseModel):
    """Response model for listing projects."""

    projects: list[ProjectResponse]
