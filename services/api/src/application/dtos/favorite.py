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
    entity_type: str = Field(..., description="Type of entity: project or space")
    entity_id: UUID = Field(..., description="ID of the favorited entity")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FavoriteListItemResponse(BaseModel):
    """Response DTO for favorite in list view.

    Favorites are only allowed for projects and spaces (not folders or pages).
    """

    id: UUID = Field(..., description="Favorite ID")
    user_id: UUID
    entity_type: str = Field(..., description="Type of entity: project or space")
    entity_id: UUID = Field(..., description="ID of the favorited entity")
    created_at: datetime
    updated_at: datetime
    node: NodeListItemResponse = Field(
        ..., description="Node data (always present for project and space favorites)"
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class FavoriteListResponse(BaseModel):
    """Response DTO for favorite list."""

    favorites: list[FavoriteListItemResponse]
    total: int = Field(..., description="Total number of favorites")


class CreateFavoriteRequest(BaseModel):
    """Request DTO for creating a favorite.

    Favorites are only allowed for projects and spaces (not folders or pages).
    """

    entity_type: Literal["project", "space"] = Field(
        ..., description="Type of entity to favorite (project or space only)"
    )
    entity_id: UUID = Field(..., description="ID of the entity to favorite")

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        """Validate entity type using EntityType value object."""
        # This will raise ValidationException if invalid
        EntityType.from_string(v)
        v_lower = v.lower().strip()
        # Ensure only project or space are allowed
        if v_lower not in ("project", "space"):
            raise ValueError("Favorites can only be created for projects or spaces")
        return v_lower
