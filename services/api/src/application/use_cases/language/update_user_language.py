"""Update user language preference use case."""

from datetime import datetime
from uuid import UUID

import structlog

from src.application.dtos.language import UpdateUserLanguageResponse, UserLanguagePreference
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import UserRepository
from src.domain.value_objects.language import Language

logger = structlog.get_logger()


class UpdateUserLanguageUseCase:
    """Use case for updating user language preference."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository

    async def execute(
        self,
        user_id: UUID,
        request: UserLanguagePreference,
    ) -> UpdateUserLanguageResponse:
        """Execute update user language preference.

        Args:
            user_id: User ID
            request: Language preference request with language code

        Returns:
            UpdateUserLanguageResponse with updated language

        Raises:
            EntityNotFoundException: If user not found
            ValueError: If language code is invalid
        """
        logger.info(
            "Updating user language preference",
            user_id=user_id,
            language=request.language,
        )

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", str(user_id))

        # Validate and create Language value object
        try:
            new_language = Language.from_string(request.language)
        except ValueError as e:
            logger.warning(
                "Invalid language code",
                user_id=user_id,
                language=request.language,
                error=str(e),
            )
            raise

        # Update user language
        user.language = new_language
        user.updated_at = datetime.utcnow()

        # Save to repository
        updated_user = await self._user_repository.update(user)

        logger.info(
            "User language preference updated",
            user_id=user_id,
            language=str(updated_user.language),
        )

        return UpdateUserLanguageResponse(
            language=str(updated_user.language),
            message="Language preference updated successfully",
        )
