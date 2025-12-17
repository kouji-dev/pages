"""Issue link DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateIssueLinkRequest(BaseModel):
    """Request DTO for creating an issue link."""

    target_issue_id: UUID = Field(..., description="Target issue ID")
    link_type: str = Field(
        ...,
        description="Link type: blocks, blocked_by, relates_to, duplicate, duplicated_by",
    )


class IssueLinkResponse(BaseModel):
    """Response DTO for issue link."""

    id: UUID
    source_issue_id: UUID
    target_issue_id: UUID
    link_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class IssueLinkListResponse(BaseModel):
    """Response DTO for issue link list."""

    links: list[IssueLinkResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True
