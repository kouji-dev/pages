"""Page and space permission DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PagePermissionResponse(BaseModel):
    """Response DTO for page permission data."""

    id: UUID
    page_id: UUID
    user_id: UUID | None = None
    role: str = Field(..., description="Permission role: read, edit, delete, admin")
    inherited_from_space: bool = Field(False, description="Whether inherited from space")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PagePermissionListResponse(BaseModel):
    """Response DTO for page permission list."""

    permissions: list[PagePermissionResponse]
    total: int = Field(..., description="Total number of permissions")


class UpdatePagePermissionRequest(BaseModel):
    """Request DTO for updating page permissions."""

    permissions: list[dict[str, UUID | str]] = Field(
        ...,
        description="List of permission assignments: [{'user_id': UUID, 'role': 'read|edit|delete|admin'}]",
    )


class SpacePermissionResponse(BaseModel):
    """Response DTO for space permission data."""

    id: UUID
    space_id: UUID
    user_id: UUID | None = None
    role: str = Field(..., description="Permission role: view, create, edit, delete, admin")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SpacePermissionListResponse(BaseModel):
    """Response DTO for space permission list."""

    permissions: list[SpacePermissionResponse]
    total: int = Field(..., description="Total number of permissions")


class UpdateSpacePermissionRequest(BaseModel):
    """Request DTO for updating space permissions."""

    permissions: list[dict[str, UUID | str]] = Field(
        ...,
        description="List of permission assignments: [{'user_id': UUID, 'role': 'view|create|edit|delete|admin'}]",
    )
