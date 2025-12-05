"""User deactivation use case."""

import structlog

from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import UserRepository

logger = structlog.get_logger()


class DeactivateUserUseCase:
    """Use case for deactivating (soft deleting) a user."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> None:
        """Execute user deactivation.

        Soft deletes the user by setting deleted_at timestamp and is_active=False.
        This will automatically invalidate all existing JWT tokens for this user
        since get_current_user checks is_active and is_deleted.

        Args:
            user_id: Current user ID

        Raises:
            EntityNotFoundException: If user not found
        """
        from uuid import UUID

        logger.info("Deactivating user", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for deactivation", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Check if already deactivated
        if user.is_deleted:
            logger.info("User already deactivated", user_id=user_id)
            return

        # Deactivate user (soft delete)
        user.deactivate()
        await self._user_repository.update(user)

        logger.info("User deactivated successfully", user_id=user_id)
