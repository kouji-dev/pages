"""User profile management use cases."""

import structlog

from src.application.dtos.user import (
    EmailUpdateRequest,
    PasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.application.interfaces import TokenService
from src.domain.entities import User
from src.domain.exceptions import (
    AuthenticationException,
    ConflictException,
    EntityNotFoundException,
    StorageException,
    ValidationException,
)
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService
from src.domain.value_objects import Email, HashedPassword, Password

logger = structlog.get_logger()


class GetUserProfileUseCase:
    """Use case for retrieving current user profile."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> UserResponse:
        """Execute get user profile.

        Args:
            user_id: Current user ID

        Returns:
            User profile response DTO

        Raises:
            EntityNotFoundException: If user not found
        """
        from uuid import UUID

        logger.info("Getting user profile", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        return UserResponse(
            id=user.id,
            email=user.email.value,
            name=user.name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UpdateUserProfileUseCase:
    """Use case for updating user profile information."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(
        self,
        user_id: str,
        request: UserUpdateRequest,
    ) -> UserResponse:
        """Execute update user profile.

        Args:
            user_id: Current user ID
            request: Update request DTO

        Returns:
            Updated user profile response DTO

        Raises:
            EntityNotFoundException: If user not found
            ValidationException: If validation fails
        """
        from uuid import UUID

        logger.info("Updating user profile", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for update", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Update name if provided
        if request.name is not None:
            if not request.name.strip():
                raise ValidationException("Name cannot be empty", field="name")
            user.update_name(request.name)

        # Persist changes
        updated_user = await self._user_repository.update(user)

        logger.info("User profile updated", user_id=user_id)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email.value,
            name=updated_user.name,
            avatar_url=updated_user.avatar_url,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )


class UpdateUserEmailUseCase:
    """Use case for updating user email address."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
            password_service: Password service for verification
        """
        self._user_repository = user_repository
        self._password_service = password_service

    async def execute(
        self,
        user_id: str,
        request: EmailUpdateRequest,
    ) -> UserResponse:
        """Execute update user email.

        Args:
            user_id: Current user ID
            request: Email update request DTO with new email and current password

        Returns:
            Updated user profile response DTO

        Raises:
            EntityNotFoundException: If user not found
            AuthenticationException: If current password is incorrect
            ConflictException: If new email already exists
            ValidationException: If email format is invalid
        """
        from uuid import UUID

        logger.info("Updating user email", user_id=user_id, new_email=request.new_email)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for email update", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Verify current password
        current_password = Password(request.current_password)
        if not self._password_service.verify(current_password.value, user.password_hash):
            logger.warning("Invalid password for email update", user_id=user_id)
            raise AuthenticationException("Invalid current password")

        # Create email value object (validates format)
        new_email = Email(request.new_email)

        # Check if new email already exists
        if await self._user_repository.exists_by_email(new_email):
            logger.warning(
                "Email update failed: email exists",
                user_id=user_id,
                new_email=request.new_email,
            )
            raise ConflictException("Email already registered", field="new_email")

        # Update email using domain method
        user.update_email(new_email)

        # Persist changes
        updated_user = await self._user_repository.update(user)

        logger.info("User email updated", user_id=user_id, new_email=request.new_email)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email.value,
            name=updated_user.name,
            avatar_url=updated_user.avatar_url,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )


class UpdateUserPasswordUseCase:
    """Use case for updating user password."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
            password_service: Password service for hashing
        """
        self._user_repository = user_repository
        self._password_service = password_service

    async def execute(
        self,
        user_id: str,
        request: PasswordUpdateRequest,
    ) -> None:
        """Execute update user password.

        Args:
            user_id: Current user ID
            request: Password update request DTO with current and new password

        Raises:
            EntityNotFoundException: If user not found
            AuthenticationException: If current password is incorrect
            ValidationException: If new password doesn't meet requirements
        """
        from uuid import UUID

        logger.info("Updating user password", user_id=user_id)

        user_uuid = UUID(user_id)
        user = await self._user_repository.get_by_id(user_uuid)

        if user is None:
            logger.warning("User not found for password update", user_id=user_id)
            raise EntityNotFoundException("User", user_id)

        # Verify current password
        current_password = Password(request.current_password)
        if not self._password_service.verify(current_password.value, user.password_hash):
            logger.warning("Invalid password for password update", user_id=user_id)
            raise AuthenticationException("Invalid current password")

        # Validate and hash new password
        new_password = Password(request.new_password)
        hashed_password = self._password_service.hash(new_password)

        # Update password
        user.update_password(hashed_password)

        # Persist changes
        await self._user_repository.update(user)

        logger.info("User password updated", user_id=user_id)

