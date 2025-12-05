"""Attachment database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.config import Base
from src.infrastructure.database.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class AttachmentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Attachment database model.
    
    Attachments can be linked to issues or pages using polymorphic association.
    """

    __tablename__ = "attachments"

    # Polymorphic association
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # 'issue' or 'page'
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    # File information
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )  # Size in bytes
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    # Storage location
    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )  # Path in storage (S3 key, local path, or pg_largeobject OID)
    storage_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="local",
    )  # 'local', 's3', 'pg_largeobject'
    
    # Thumbnail for images
    thumbnail_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Uploader
    uploaded_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, name={self.file_name}, type={self.mime_type})>"

