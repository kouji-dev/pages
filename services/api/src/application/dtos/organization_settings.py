"""Organization settings DTOs."""

from typing import Any

from pydantic import BaseModel, Field


class OrganizationSettingsResponse(BaseModel):
    """Response DTO for organization settings."""

    settings: dict[str, Any] = Field(
        ..., description="Organization settings dictionary with feature flags, notifications, and branding"
    )


class UpdateOrganizationSettingsRequest(BaseModel):
    """Request DTO for updating organization settings.

    All fields are optional - only provided fields will be updated.
    Settings are merged with existing settings (not replaced).
    """

    settings: dict[str, Any] = Field(
        ..., description="Settings dictionary to update (will be merged with existing settings)"
    )

