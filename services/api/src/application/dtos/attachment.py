"""Attachment DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    """Response DTO for attachment data."""

    id: UUID
    entity_type: str = Field(..., description="Entity type: issue or page")
    entity_id: UUID
    file_name: str = Field(..., description="Unique filename in storage")
    original_name: str = Field(..., description="Original filename from user")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    storage_path: str = Field(..., description="Path in storage")
    storage_type: str = Field(default="local", description="Storage type: local, s3, etc.")
    thumbnail_path: str | None = Field(None, description="Thumbnail path for images")
    uploaded_by: UUID | None = Field(None, description="ID of the user who uploaded the file")
    uploader_name: str | None = Field(None, description="Name of the user who uploaded")
    uploader_email: str | None = Field(None, description="Email of the user who uploaded")
    download_url: str | None = Field(None, description="URL to download the file")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AttachmentListItemResponse(BaseModel):
    """Response DTO for attachment in list view."""

    id: UUID
    entity_type: str
    entity_id: UUID
    file_name: str
    original_name: str
    file_size: int
    mime_type: str
    storage_path: str
    storage_type: str
    thumbnail_path: str | None = None
    uploaded_by: UUID | None = None
    uploader_name: str | None = None
    uploader_email: str | None = None
    download_url: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Response DTO for list of attachments."""

    attachments: list[AttachmentListItemResponse] = Field(
        ..., description="List of attachments"
    )
    total: int = Field(..., description="Total number of attachments")


class UploadAttachmentResponse(BaseModel):
    """Response DTO for file upload."""

    id: UUID
    entity_type: str
    entity_id: UUID
    file_name: str
    original_name: str
    file_size: int
    mime_type: str
    storage_path: str
    storage_type: str
    thumbnail_path: str | None = None
    uploaded_by: UUID | None = None
    uploader_name: str | None = None
    uploader_email: str | None = None
    download_url: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True

