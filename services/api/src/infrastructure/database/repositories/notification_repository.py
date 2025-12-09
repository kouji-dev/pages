"""SQLAlchemy implementation of NotificationRepository."""

import json
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Notification
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories.notification_repository import NotificationRepository
from src.domain.value_objects.notification_type import NotificationType
from src.infrastructure.database.models import NotificationModel


class SQLAlchemyNotificationRepository(NotificationRepository):
    """SQLAlchemy implementation of NotificationRepository.

    Adapts the domain NotificationRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        """Create a new notification in the database.

        Args:
            notification: Notification domain entity

        Returns:
            Created notification with persisted data
        """
        # Serialize data dict to JSON string
        data_json = json.dumps(notification.data) if notification.data else None

        # Create model from entity
        model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type.value,
            title=notification.title,
            content=notification.content,
            entity_type=notification.entity_type,
            entity_id=notification.entity_id,
            read=notification.read,
            data=data_json,
            created_at=notification.created_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        """Get notification by ID.

        Args:
            notification_id: Notification UUID

        Returns:
            Notification if found, None otherwise
        """
        result = await self._session.execute(
            select(NotificationModel).where(NotificationModel.id == notification_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, notification: Notification) -> Notification:
        """Update an existing notification.

        Args:
            notification: Notification entity with updated data

        Returns:
            Updated notification

        Raises:
            EntityNotFoundException: If notification not found
        """
        result = await self._session.execute(
            select(NotificationModel).where(NotificationModel.id == notification.id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Notification", str(notification.id))

        # Serialize data dict to JSON string
        data_json = json.dumps(notification.data) if notification.data else None

        # Update model fields
        model.type = notification.type.value
        model.title = notification.title
        model.content = notification.content
        model.entity_type = notification.entity_type
        model.entity_id = notification.entity_id
        model.read = notification.read
        model.data = data_json

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, notification_id: UUID) -> None:
        """Hard delete a notification.

        Args:
            notification_id: Notification UUID

        Raises:
            EntityNotFoundException: If notification not found
        """
        result = await self._session.execute(
            select(NotificationModel).where(NotificationModel.id == notification_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Notification", str(notification_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_by_user_id(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        read: bool | None = None,
    ) -> list[Notification]:
        """Get all notifications for a user.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            read: Filter by read status (None = all, True = read only, False = unread only)

        Returns:
            List of notifications, ordered by created_at DESC
        """
        query = select(NotificationModel).where(NotificationModel.user_id == user_id)

        # Apply read filter if provided
        if read is not None:
            query = query.where(NotificationModel.read == read)

        # Order by created_at descending (newest first)
        query = query.order_by(NotificationModel.created_at.desc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count_by_user_id(self, user_id: UUID, read: bool | None = None) -> int:
        """Count total notifications for a user.

        Args:
            user_id: User UUID
            read: Filter by read status (None = all, True = read only, False = unread only)

        Returns:
            Total count of notifications
        """
        query = select(func.count(NotificationModel.id)).where(NotificationModel.user_id == user_id)

        # Apply read filter if provided
        if read is not None:
            query = query.where(NotificationModel.read == read)

        result = await self._session.execute(query)
        return result.scalar_one()

    async def mark_as_read(self, notification_id: UUID) -> Notification:
        """Mark notification as read.

        Args:
            notification_id: Notification UUID

        Returns:
            Updated notification

        Raises:
            EntityNotFoundException: If notification not found
        """
        result = await self._session.execute(
            select(NotificationModel).where(NotificationModel.id == notification_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Notification", str(notification_id))

        model.read = True
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications marked as read
        """
        result = await self._session.execute(
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.read == False,  # noqa: E712
            )
            .values(read=True)
        )
        await self._session.flush()

        # Return the number of updated rows
        return result.rowcount  # type: ignore

    async def count_unread(self, user_id: UUID) -> int:
        """Count unread notifications for a user.

        Args:
            user_id: User UUID

        Returns:
            Count of unread notifications
        """
        result = await self._session.execute(
            select(func.count(NotificationModel.id)).where(
                NotificationModel.user_id == user_id,
                NotificationModel.read == False,  # noqa: E712
            )
        )
        return result.scalar_one()

    def _to_entity(self, model: NotificationModel) -> Notification:
        """Convert database model to domain entity.

        Args:
            model: Database model

        Returns:
            Domain entity
        """
        # Deserialize data JSON string to dict
        data_dict = json.loads(model.data) if model.data else None

        return Notification(
            id=model.id,
            user_id=model.user_id,
            type=NotificationType(model.type),
            title=model.title,
            content=model.content,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            read=model.read,
            data=data_dict,
            created_at=model.created_at,
        )
