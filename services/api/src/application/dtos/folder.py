"""Folder DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FolderResponse(BaseModel):
    """Response DTO for folder data."""

    id: UUID
    organization_id: UUID
    name: str
    parent_id: UUID | None = None
    position: int = Field(0, description="Position/order for display")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FolderListItemResponse(BaseModel):
    """Response DTO for folder in list view."""

    id: UUID
    organization_id: UUID
    name: str
    parent_id: UUID | None = None
    position: int = Field(0, description="Position/order for display")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FolderListResponse(BaseModel):
    """Response DTO for folder list."""

    folders: list[FolderListItemResponse]
    total: int = Field(..., description="Total number of folders")


class CreateFolderRequest(BaseModel):
    """Request DTO for creating a folder."""

    organization_id: UUID = Field(..., description="ID of the organization")
    name: str = Field(..., min_length=1, max_length=100, description="Folder name")
    parent_id: UUID | None = Field(None, description="Optional parent folder ID for hierarchy")
    position: int = Field(0, ge=0, description="Position/order for display")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()


class UpdateFolderRequest(BaseModel):
    """Request DTO for updating a folder."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Folder name")
    parent_id: UUID | None = Field(
        None, description="Optional parent folder ID for hierarchy (None for root level)"
    )
    position: int | None = Field(None, ge=0, description="Position/order for display")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is not None:
            return v.strip()
        return v


class AssignNodesToFolderRequest(BaseModel):
    """Request DTO for assigning nodes to a folder."""

    node_ids: list[UUID] = Field(..., description="List of node IDs (projects or spaces) to assign")
