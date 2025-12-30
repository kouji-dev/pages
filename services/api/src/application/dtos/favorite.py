"""Favorite DTOs."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.application.dtos.node import NodeListItemResponse
from src.domain.value_objects.entity_type import EntityType


class FavoriteResponse(BaseModel):
    """Response DTO for favorite data."""

    id: UUID
    user_id: UUID
    entity_type: str = Field(..., description="Type of entity: project, space, or page")
    entity_id: UUID = Field(..., description="ID of the favorited entity")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FavoriteListItemResponse(BaseModel):
    """Response DTO for favorite in list view."""

    id: UUID = Field(..., description="Favorite ID")
    user_id: UUID
    entity_type: str = Field(..., description="Type of entity: project, space, or page")
    entity_id: UUID = Field(..., description="ID of the favorited entity")
    created_at: datetime
    updated_at: datetime
    node: NodeListItemResponse | None = Field(
        None, description="Node data (for project and space types only)"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class FavoriteListResponse(BaseModel):
    """Response DTO for favorite list."""

    favorites: list[FavoriteListItemResponse]
    total: int = Field(..., description="Total number of favorites")


class CreateFavoriteRequest(BaseModel):
    """Request DTO for creating a favorite."""

    entity_type: Literal["project", "space", "page"] = Field(
        ..., description="Type of entity to favorite"
    )
    entity_id: UUID = Field(..., description="ID of the entity to favorite")

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        """Validate entity type using EntityType value object."""
        # This will raise ValidationException if invalid
        EntityType.from_string(v)
        return v.lower().strip()
