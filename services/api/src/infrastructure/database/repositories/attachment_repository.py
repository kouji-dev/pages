"""SQLAlchemy implementation of AttachmentRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Attachment
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.attachment_repository import AttachmentRepository
from src.infrastructure.database.models import AttachmentModel


class SQLAlchemyAttachmentRepository(AttachmentRepository):
    """SQLAlchemy implementation of AttachmentRepository.

    Adapts the domain AttachmentRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, attachment: Attachment) -> Attachment:
        """Create a new attachment in the database.

        Args:
            attachment: Attachment domain entity

        Returns:
            Created attachment with persisted data
        """
        # Create model from entity
        model = AttachmentModel(
            id=attachment.id,
            entity_type=attachment.entity_type,
            entity_id=attachment.entity_id,
            file_name=attachment.file_name,
            original_name=attachment.original_name,
            file_size=attachment.file_size,
            mime_type=attachment.mime_type,
            storage_path=attachment.storage_path,
            storage_type=attachment.storage_type,
            thumbnail_path=attachment.thumbnail_path,
            uploaded_by=attachment.uploaded_by,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, attachment_id: UUID) -> Attachment | None:
        """Get attachment by ID.

        Args:
            attachment_id: Attachment UUID

        Returns:
            Attachment if found, None otherwise
        """
        result = await self._session.execute(
            select(AttachmentModel).where(AttachmentModel.id == attachment_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def delete(self, attachment_id: UUID) -> None:
        """Hard delete an attachment.

        Args:
            attachment_id: Attachment UUID

        Raises:
            EntityNotFoundException: If attachment not found
        """
        result = await self._session.execute(
            select(AttachmentModel).where(AttachmentModel.id == attachment_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Attachment", str(attachment_id))

        await self._session.delete(model)
        await self._session.flush()

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
        result = await self._session.execute(
            select(AttachmentModel)
            .where(
                AttachmentModel.entity_type == entity_type,
                AttachmentModel.entity_id == entity_id,
            )
            .order_by(AttachmentModel.created_at.asc())
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: AttachmentModel) -> Attachment:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy AttachmentModel

        Returns:
            Attachment domain entity
        """
        return Attachment(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            file_name=model.file_name,
            original_name=model.original_name,
            file_size=model.file_size,
            mime_type=model.mime_type,
            storage_path=model.storage_path,
            storage_type=model.storage_type,
            thumbnail_path=model.thumbnail_path,
            uploaded_by=model.uploaded_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

