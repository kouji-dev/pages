"""Get user language preference use case."""

from uuid import UUID

import structlog

from src.application.dtos.language import UserLanguageResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import UserRepository

logger = structlog.get_logger()


class GetUserLanguageUseCase:
    """Use case for retrieving user language preference."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> UserLanguageResponse:
        """Execute get user language preference.

        Args:
            user_id: User ID

        Returns:
            UserLanguageResponse with current language preference

        Raises:
            EntityNotFoundException: If user not found
        """
        logger.info("Getting user language preference", user_id=user_id)

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", str(user_id))

        logger.info(
            "User language preference retrieved",
            user_id=user_id,
            language=str(user.language),
        )

        return UserLanguageResponse(
            language=str(user.language),
            message="Language preference retrieved successfully",
        )
