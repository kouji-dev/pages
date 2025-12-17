"""Unified DTOs for folders and nodes (projects + spaces)."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Constants for item types (no hardcoding)
ITEM_TYPE_FOLDER = "folder"
ITEM_TYPE_PROJECT = "project"
ITEM_TYPE_SPACE = "space"


class DTOResponseFolder(BaseModel):
    """Response DTO for folder details."""

    name: str = Field(..., min_length=1, max_length=100, description="Folder name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    class Config:
        """Pydantic config."""

        from_attributes = True


class DTOResponseProject(BaseModel):
    """Response DTO for project details."""

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    key: str | None = Field(None, description="Project key")
    description: str | None = Field(None, max_length=1000, description="Project description")
    folder_id: UUID | None = Field(None, description="Folder ID if assigned to a folder")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    class Config:
        """Pydantic config."""

        from_attributes = True


class DTOResponseSpace(BaseModel):
    """Response DTO for space details."""

    name: str = Field(..., min_length=1, max_length=100, description="Space name")
    key: str | None = Field(None, description="Space key")
    description: str | None = Field(None, max_length=1000, description="Space description")
    folder_id: UUID | None = Field(None, description="Folder ID if assigned to a folder")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    class Config:
        """Pydantic config."""

        from_attributes = True


class DTOItemFolder(BaseModel):
    """Response DTO for folder item in unified list."""

    type: Literal["folder"] = Field(..., description=f"Item type: {ITEM_TYPE_FOLDER}")
    id: UUID = Field(..., description="Folder ID")
    organization_id: UUID = Field(..., description="Organization ID")
    position: int = Field(..., ge=0, description="Position/order for display")
    details: DTOResponseFolder = Field(..., description="Folder details")

    class Config:
        """Pydantic config."""

        from_attributes = True


class DTOItemProject(BaseModel):
    """Response DTO for project item in unified list."""

    type: Literal["project"] = Field(..., description=f"Item type: {ITEM_TYPE_PROJECT}")
    id: UUID = Field(..., description="Project ID")
    organization_id: UUID = Field(..., description="Organization ID")
    details: DTOResponseProject = Field(..., description="Project details")

    class Config:
        """Pydantic config."""

        from_attributes = True


class DTOItemSpace(BaseModel):
    """Response DTO for space item in unified list."""

    type: Literal["space"] = Field(..., description=f"Item type: {ITEM_TYPE_SPACE}")
    id: UUID = Field(..., description="Space ID")
    organization_id: UUID = Field(..., description="Organization ID")
    details: DTOResponseSpace = Field(..., description="Space details")

    class Config:
        """Pydantic config."""

        from_attributes = True


class UnifiedListResponse(BaseModel):
    """Response DTO for unified folders and nodes list."""

    items: list[DTOItemFolder | DTOItemProject | DTOItemSpace] = Field(
        ..., description="List of folders and nodes"
    )
    folders_count: int = Field(..., ge=0, description="Number of folders in the list")
    nodes_count: int = Field(
        ..., ge=0, description="Number of nodes (projects + spaces) in the list"
    )
    total: int = Field(..., ge=0, description="Total number of items")

    class Config:
        """Pydantic config."""

        from_attributes = True
