"""Board DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BoardListColumnResponse(BaseModel):
    """Response DTO for a board list (column)."""

    id: UUID
    board_id: UUID
    list_type: str = Field(..., description="label, assignee, or milestone")
    list_config: dict[str, Any] | None = None
    position: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardResponse(BaseModel):
    """Response DTO for board (without lists)."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardWithListsResponse(BaseModel):
    """Response DTO for board including its lists."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    lists: list[BoardListColumnResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListItemResponse(BaseModel):
    """Response DTO for board in list view."""

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListResponse(BaseModel):
    """Response DTO for paginated board list."""

    boards: list[BoardListItemResponse]
    total: int = Field(..., description="Total number of boards")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateBoardRequest(BaseModel):
    """Request DTO for creating a board."""

    name: str = Field(..., min_length=1, max_length=255, description="Board name")
    description: str | None = Field(None, max_length=65535, description="Board description")
    scope_config: dict[str, Any] | None = Field(None, description="Scope filters (e.g. label_ids)")
    is_default: bool = False
    position: int = Field(0, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        v = v.strip()
        if not v:
            raise ValueError("Board name cannot be empty")
        return v


class UpdateBoardRequest(BaseModel):
    """Request DTO for updating a board."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=65535)
    scope_config: dict[str, Any] | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Board name cannot be empty")
        return v
