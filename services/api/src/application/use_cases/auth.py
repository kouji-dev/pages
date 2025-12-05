"""Authentication use cases."""

import structlog

from src.application.dtos import (
    LoginRequest,
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.application.dtos.auth import UserBasicInfo
from src.application.interfaces import TokenService
from src.domain.entities import User
from src.domain.exceptions import (
    AuthenticationException,
    ConflictException,
    EntityNotFoundException,
)
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService
from src.domain.value_objects import Email, Password

logger = structlog.get_logger()


class RegisterUserUseCase:
    """Use case for user registration."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, request: RegisterRequest) -> RegisterResponse:
        """Execute user registration.

        Args:
            request: Registration request DTO

        Returns:
            Registration response with tokens

        Raises:
            ConflictException: If email already exists
            ValidationException: If validation fails
        """
        logger.info("Registering new user", email=request.email)

        # Create email value object (validates format)
        email = Email(request.email)

        # Check if email already exists
        if await self._user_repository.exists_by_email(email):
            logger.warning("Registration failed: email exists", email=request.email)
            raise ConflictException("Email already registered", field="email")

        # Create password value object (validates strength)
        password = Password(request.password)

        # Hash the password
        hashed_password = self._password_service.hash(password)

        # Create user entity
        user = User.create(
            email=email,
            password_hash=hashed_password,
            name=request.name,
        )

        # Persist user
        created_user = await self._user_repository.create(user)

        # Generate tokens
        access_token = self._token_service.create_access_token(created_user.id)
        refresh_token = self._token_service.create_refresh_token(created_user.id)

        logger.info("User registered successfully", user_id=str(created_user.id))

        return RegisterResponse(
            id=created_user.id,
            email=str(created_user.email),
            name=created_user.name,
            access_token=access_token,
            refresh_token=refresh_token,
        )


class LoginUserUseCase:
    """Use case for user login."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, request: LoginRequest) -> LoginResponse:
        """Execute user login.

        Args:
            request: Login request DTO

        Returns:
            Login response with tokens and user info

        Raises:
            AuthenticationException: If credentials are invalid
        """
        logger.info("User login attempt", email=request.email)

        # Get user by email
        email = Email(request.email)
        user = await self._user_repository.get_by_email(email)

        if user is None:
            logger.warning("Login failed: user not found", email=request.email)
            raise AuthenticationException("Invalid email or password")

        # Check if user is active
        if not user.is_active or user.is_deleted:
            logger.warning("Login failed: user inactive", email=request.email)
            raise AuthenticationException("Account is deactivated")

        # Verify password
        if not self._password_service.verify(request.password, user.password_hash):
            logger.warning("Login failed: invalid password", email=request.email)
            raise AuthenticationException("Invalid email or password")

        # Generate tokens
        access_token = self._token_service.create_access_token(user.id)
        refresh_token = self._token_service.create_refresh_token(user.id)

        logger.info("User logged in successfully", user_id=str(user.id))

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_service.access_token_expire_minutes * 60,
            user=UserBasicInfo(
                id=user.id,
                email=str(user.email),
                name=user.name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified,
            ),
        )


class RefreshTokenUseCase:
    """Use case for refreshing access token."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    async def execute(self, request: RefreshTokenRequest) -> TokenResponse:
        """Execute token refresh.

        Args:
            request: Refresh token request DTO

        Returns:
            New tokens

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        # Verify refresh token and get user ID
        user_id = self._token_service.get_user_id_from_token(request.refresh_token)

        # Verify user still exists and is active
        user = await self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active or user.is_deleted:
            raise AuthenticationException("Invalid refresh token")

        # Generate new tokens
        access_token = self._token_service.create_access_token(user.id)
        refresh_token = self._token_service.create_refresh_token(user.id)

        logger.info("Token refreshed", user_id=str(user_id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._token_service.access_token_expire_minutes * 60,
        )


class RequestPasswordResetUseCase:
    """Use case for requesting password reset."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
        # email_service: EmailService,  # TODO: Add when email service is implemented
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    async def execute(self, request: PasswordResetRequest) -> None:
        """Execute password reset request.

        Always returns success to prevent email enumeration.

        Args:
            request: Password reset request DTO
        """
        logger.info("Password reset requested", email=request.email)

        try:
            email = Email(request.email)
        except Exception:
            # Invalid email format, but don't reveal this
            return

        user = await self._user_repository.get_by_email(email)

        if user is None or not user.is_active:
            # User not found or inactive, but don't reveal this
            logger.info("Password reset: user not found", email=request.email)
            return

        # Generate password reset token
        _reset_token = self._token_service.create_password_reset_token(user.id)

        # TODO: Send email with reset token
        # await self._email_service.send_password_reset(user.email, _reset_token)

        logger.info("Password reset token generated", user_id=str(user.id))


class ResetPasswordUseCase:
    """Use case for resetting password with token."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, request: PasswordResetConfirm) -> None:
        """Execute password reset.

        Args:
            request: Password reset confirmation DTO

        Raises:
            AuthenticationException: If token is invalid
            EntityNotFoundException: If user not found
        """
        # Verify token and get user ID
        user_id = self._token_service.verify_password_reset_token(request.token)

        # Get user
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            raise EntityNotFoundException("User", str(user_id))

        # Validate and hash new password
        password = Password(request.new_password)
        hashed_password = self._password_service.hash(password)

        # Update user password
        user.update_password(hashed_password)
        await self._user_repository.update(user)

        logger.info("Password reset successful", user_id=str(user_id))
