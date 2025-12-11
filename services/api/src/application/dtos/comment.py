"""Comment DTOs.

Follows Clean Architecture and DDD principles:
- Uses UserDTO for embedded user information
- Eliminates field duplication
- Provides rich read models for the UI
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .user import UserDTO


class CommentResponse(BaseModel):
    """Response DTO for comment data.

    Includes embedded UserDTO to provide author information without
    requiring additional queries. This is essential for rendering
    comment threads efficiently.
    """

    id: UUID
    entity_type: str = Field(..., description="Entity type: issue or page")
    entity_id: UUID
    issue_id: UUID | None = None
    page_id: UUID | None = None

    # User reference and embedded data
    user_id: UUID
    user: UserDTO = Field(..., description="Comment author information")

    content: str
    is_edited: bool = Field(default=False, description="Whether the comment has been edited")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CommentListItemResponse(BaseModel):
    """Response DTO for comment in list view.

    Optimized for comment threads with embedded author information.
    """

    id: UUID
    entity_type: str
    entity_id: UUID
    issue_id: UUID | None = None
    page_id: UUID | None = None

    # User reference and embedded data
    user_id: UUID
    user: UserDTO = Field(..., description="Comment author information")

    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CommentListResponse(BaseModel):
    """Response DTO for list of comments."""

    comments: list[CommentListItemResponse] = Field(..., description="List of comments")
    total: int = Field(..., description="Total number of comments")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class CreateCommentRequest(BaseModel):
    """Request DTO for creating a comment."""

    content: str = Field(..., description="Comment content", min_length=1, max_length=10000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v.strip()


class UpdateCommentRequest(BaseModel):
    """Request DTO for updating a comment."""

    content: str = Field(..., description="Comment content", min_length=1, max_length=10000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v.strip()
