"""Issue activity DTOs.

Follows Clean Architecture and DDD principles:
- Uses UserDTO for actor information
- Provides audit trail with rich user context
- Optimized read model for activity feeds
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .user import UserDTO


class IssueActivityResponse(BaseModel):
    """Response DTO for issue activity data.

    Provides complete activity information with embedded user data
    for rendering activity feeds and audit trails.

    The user can be None for system-generated activities.
    """

    id: UUID
    issue_id: UUID

    # User reference and embedded data (optional for system actions)
    user_id: UUID | None = None
    user: UserDTO | None = Field(None, description="User who performed the action")

    action: str = Field(..., description="Action type: created, updated, deleted, etc.")
    field_name: str | None = Field(None, description="Field name that was changed")
    old_value: str | None = Field(None, description="Previous value")
    new_value: str | None = Field(None, description="New value")
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
