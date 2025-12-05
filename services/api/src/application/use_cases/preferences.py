"""User preferences management use cases."""

import structlog

from src.application.dtos.preferences import UserPreferencesResponse, UserPreferencesUpdateRequest
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import UserRepository
from src.domain.value_objects.preferences import get_default_preferences

logger = structlog.get_logger()


class GetUserPreferencesUseCase:
    """Use case for retrieving current user preferences."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> UserPreferencesResponse:
        """Execute get user preferences.

        Args:
            user_id: Current user ID

        Returns:
            User preferences response DTO

        Raises:
            EntityNotFoundException: If user not found
        """
        from uuid import UUID

        logger.info("Getting user preferences", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for preferences", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Use user preferences or defaults
        preferences = user.preferences or get_default_preferences()

        # Build response DTO
        from src.application.dtos.preferences import AllNotificationPreferences, NotificationPreferences

        notification_prefs = preferences.get("notifications", {})

        return UserPreferencesResponse(
            theme=preferences.get("theme", "auto"),
            language=preferences.get("language", "en"),
            notifications=AllNotificationPreferences(
                email=NotificationPreferences(**notification_prefs.get("email", {})),
                push=NotificationPreferences(**notification_prefs.get("push", {})),
                in_app=NotificationPreferences(**notification_prefs.get("in_app", {})),
            ),
        )


class UpdateUserPreferencesUseCase:
    """Use case for updating user preferences."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(
        self, user_id: str, request: UserPreferencesUpdateRequest
    ) -> UserPreferencesResponse:
        """Execute update user preferences.

        Args:
            user_id: Current user ID
            request: Preferences update request

        Returns:
            Updated user preferences response DTO

        Raises:
            EntityNotFoundException: If user not found
            ValidationException: If preferences validation fails
        """
        from uuid import UUID

        logger.info("Updating user preferences", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for preferences update", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Build preferences dictionary from request
        preferences_update: dict[str, Any] = {}

        if request.theme is not None:
            preferences_update["theme"] = request.theme

        if request.language is not None:
            preferences_update["language"] = request.language

        if request.notifications is not None:
            preferences_update["notifications"] = request.notifications

        # Update preferences (validation happens in domain entity)
        try:
            user.update_preferences(preferences_update)
        except ValueError as e:
            logger.warning("Invalid preferences", user_id=user_id, error=str(e))
            raise ValidationException(str(e), field="preferences") from e

        # Save to database
        updated_user = await self._user_repository.update(user)

        logger.info("User preferences updated", user_id=user_id)

        # Build response DTO
        preferences = updated_user.preferences or get_default_preferences()

        from src.application.dtos.preferences import AllNotificationPreferences, NotificationPreferences

        notification_prefs = preferences.get("notifications", {})

        return UserPreferencesResponse(
            theme=preferences.get("theme", "auto"),
            language=preferences.get("language", "en"),
            notifications=AllNotificationPreferences(
                email=NotificationPreferences(**notification_prefs.get("email", {})),
                push=NotificationPreferences(**notification_prefs.get("push", {})),
                in_app=NotificationPreferences(**notification_prefs.get("in_app", {})),
            ),
        )

