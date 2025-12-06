"""Issue activity DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IssueActivityResponse(BaseModel):
    """Response DTO for issue activity data."""

    id: UUID
    issue_id: UUID
    user_id: UUID | None = None
    action: str = Field(..., description="Action type: created, updated, deleted, etc.")
    field_name: str | None = Field(None, description="Field name that was changed")
    old_value: str | None = Field(None, description="Previous value")
    new_value: str | None = Field(None, description="New value")
    user_name: str | None = Field(None, description="User name who performed the action")
    user_email: str | None = Field(None, description="User email who performed the action")
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class IssueActivityListResponse(BaseModel):
    """Response DTO for list of issue activities."""

    activities: list[IssueActivityResponse] = Field(..., description="List of activities")
    total: int = Field(..., description="Total number of activities")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
