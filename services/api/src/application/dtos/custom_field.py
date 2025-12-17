"""Custom field DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CustomFieldRequest(BaseModel):
    """Request DTO for creating a custom field."""

    name: str = Field(..., min_length=1, max_length=100, description="Field name")
    type: str = Field(
        ...,
        description="Field type: text, number, date, select, multi_select, user, users",
    )
    is_required: bool = Field(default=False, description="Whether the field is required")
    default_value: Any | None = Field(default=None, description="Default value for the field")
    options: list[str] | None = Field(
        default=None, description="Options for select/multi_select types"
    )


class UpdateCustomFieldRequest(BaseModel):
    """Request DTO for updating a custom field."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Field name")
    is_required: bool | None = Field(None, description="Whether the field is required")
    default_value: Any | None = Field(None, description="Default value for the field")
    options: list[str] | None = Field(None, description="Options for select/multi_select types")


class CustomFieldResponse(BaseModel):
    """Response DTO for custom field."""

    id: UUID
    project_id: UUID
    name: str
    type: str
    is_required: bool
    default_value: Any | None
    options: list[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomFieldListResponse(BaseModel):
    """Response DTO for custom field list."""

    fields: list[CustomFieldResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomFieldValueRequest(BaseModel):
    """Request DTO for creating/updating a custom field value."""

    custom_field_id: UUID = Field(..., description="Custom field ID")
    value: Any = Field(..., description="Field value")


class CustomFieldValueResponse(BaseModel):
    """Response DTO for custom field value."""

    id: UUID
    custom_field_id: UUID
    issue_id: UUID
    value: Any
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomFieldValueListResponse(BaseModel):
    """Response DTO for custom field value list."""

    values: list[CustomFieldValueResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True
