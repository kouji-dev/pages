"""Comment DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CommentResponse(BaseModel):
    """Response DTO for comment data."""

    id: UUID
    entity_type: str = Field(..., description="Entity type: issue or page")
    entity_id: UUID
    issue_id: UUID | None = None
    user_id: UUID
    content: str
    is_edited: bool = Field(default=False, description="Whether the comment has been edited")
    user_name: str = Field(..., description="User name who created the comment")
    user_email: str = Field(..., description="User email who created the comment")
    avatar_url: str | None = Field(None, description="User avatar URL")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CommentListItemResponse(BaseModel):
    """Response DTO for comment in list view."""

    id: UUID
    entity_type: str
    entity_id: UUID
    issue_id: UUID | None = None
    user_id: UUID
    content: str
    is_edited: bool
    user_name: str
    user_email: str
    avatar_url: str | None = None
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

