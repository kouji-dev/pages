"""Attachment repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Attachment


class AttachmentRepository(ABC):
    """Abstract attachment repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, attachment: Attachment) -> Attachment:
        """Create a new attachment.

        Args:
            attachment: Attachment entity to create

        Returns:
            Created attachment with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, attachment_id: UUID) -> Attachment | None:
        """Get attachment by ID.

        Args:
            attachment_id: Attachment UUID

        Returns:
            Attachment if found, None otherwise
        """
        ...

    @abstractmethod
    async def delete(self, attachment_id: UUID) -> None:
        """Hard delete an attachment.

        Args:
            attachment_id: Attachment UUID

        Raises:
            EntityNotFoundException: If attachment not found
        """
        ...

    @abstractmethod
    async def get_by_entity_id(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> list[Attachment]:
        """Get all attachments for an entity.

        Args:
            entity_type: Type of entity ('issue' or 'page')
            entity_id: Entity UUID

        Returns:
            List of attachments, ordered by created_at ASC
        """
        ...
