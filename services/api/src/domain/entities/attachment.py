"""Attachment domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Attachment:
    """Attachment domain entity.

    Represents a file attachment on an issue or page.
    """

    id: UUID
    entity_type: str  # 'issue' or 'page'
    entity_id: UUID
    file_name: str  # Unique filename in storage
    original_name: str  # Original filename from user
    file_size: int  # Size in bytes
    mime_type: str
    storage_path: str  # Path in storage
    storage_type: str = "local"  # 'local', 's3', 'pg_largeobject'
    thumbnail_path: str | None = None
    uploaded_by: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate attachment entity."""
        valid_entity_types = {"issue", "page"}
        if self.entity_type not in valid_entity_types:
            raise ValueError(
                f"Entity type must be one of: {', '.join(valid_entity_types)}"
            )

        if not self.file_name or not self.file_name.strip():
            raise ValueError("File name cannot be empty")

        if not self.original_name or not self.original_name.strip():
            raise ValueError("Original name cannot be empty")

        if self.file_size < 0:
            raise ValueError("File size cannot be negative")

        if not self.mime_type or not self.mime_type.strip():
            raise ValueError("MIME type cannot be empty")

        if not self.storage_path or not self.storage_path.strip():
            raise ValueError("Storage path cannot be empty")

        valid_storage_types = {"local", "s3", "pg_largeobject"}
        if self.storage_type not in valid_storage_types:
            raise ValueError(
                f"Storage type must be one of: {', '.join(valid_storage_types)}"
            )

    @classmethod
    def create(
        cls,
        entity_type: str,
        entity_id: UUID,
        file_name: str,
        original_name: str,
        file_size: int,
        mime_type: str,
        storage_path: str,
        storage_type: str = "local",
        thumbnail_path: str | None = None,
        uploaded_by: UUID | None = None,
    ) -> Self:
        """Create a new attachment.

        Factory method for creating new attachments.

        Args:
            entity_type: Type of entity ('issue' or 'page')
            entity_id: ID of the entity being attached to
            file_name: Unique filename in storage
            original_name: Original filename from user
            file_size: Size in bytes
            mime_type: MIME type of the file
            storage_path: Path in storage
            storage_type: Type of storage ('local', 's3', 'pg_largeobject')
            thumbnail_path: Optional thumbnail path for images
            uploaded_by: ID of the user who uploaded the file

        Returns:
            New Attachment instance

        Raises:
            ValueError: If any parameter is invalid
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file_name,
            original_name=original_name,
            file_size=file_size,
            mime_type=mime_type,
            storage_path=storage_path,
            storage_type=storage_type,
            thumbnail_path=thumbnail_path,
            uploaded_by=uploaded_by,
            created_at=now,
            updated_at=now,
        )

