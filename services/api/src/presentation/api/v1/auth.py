"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

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
from src.application.interfaces import TokenService
from src.application.use_cases import (
    LoginUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from src.domain.repositories import UserRepository
from src.domain.services import PasswordService
from src.presentation.dependencies import (
    get_password_service,
    get_token_service,
    get_user_repository,
)
from src.presentation.middlewares import limiter

router = APIRouter()


# Dependency injection for use cases
def get_register_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> RegisterUserUseCase:
    """Get register use case with dependencies."""
    return RegisterUserUseCase(user_repository, password_service, token_service)


def get_login_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LoginUserUseCase:
    """Get login use case with dependencies."""
    return LoginUserUseCase(user_repository, password_service, token_service)


def get_refresh_token_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> RefreshTokenUseCase:
    """Get refresh token use case with dependencies."""
    return RefreshTokenUseCase(user_repository, token_service)


def get_request_password_reset_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> RequestPasswordResetUseCase:
    """Get request password reset use case with dependencies."""
    return RequestPasswordResetUseCase(user_repository, token_service)


def get_reset_password_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_service: Annotated[PasswordService, Depends(get_password_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> ResetPasswordUseCase:
    """Get reset password use case with dependencies."""
    return ResetPasswordUseCase(user_repository, password_service, token_service)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
)
@limiter.limit("5/minute")  # Strict rate limit for registration
async def register(
    http_request: Request,
    request: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
) -> RegisterResponse:
    """Register a new user.

    Args:
        request: Registration request with email, password, and name
        use_case: Register use case

    Returns:
        Registration response with user info and tokens
    """
    return await use_case.execute(request)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user with email and password.",
)
@limiter.limit("10/minute")  # Rate limit for login to prevent brute force
async def login(
    http_request: Request,
    request: LoginRequest,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_use_case)],
) -> LoginResponse:
    """Login user.

    Args:
        request: Login request with email and password
        use_case: Login use case

    Returns:
        Login response with user info and tokens
    """
    return await use_case.execute(request)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)],
) -> TokenResponse:
    """Refresh access token.

    Args:
        request: Refresh token request
        use_case: Refresh token use case

    Returns:
        New access and refresh tokens
    """
    return await use_case.execute(request)


@router.post(
    "/password/reset-request",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request password reset",
    description="Request a password reset email. Always returns success to prevent email enumeration.",
)
@limiter.limit("3/minute")  # Strict rate limit to prevent abuse
async def request_password_reset(
    http_request: Request,
    request: PasswordResetRequest,
    use_case: Annotated[RequestPasswordResetUseCase, Depends(get_request_password_reset_use_case)],
) -> dict[str, str]:
    """Request password reset.

    Args:
        request: Password reset request with email
        use_case: Request password reset use case

    Returns:
        Success message (always, to prevent email enumeration)
    """
    await use_case.execute(request)
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post(
    "/password/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using the token received via email.",
)
async def reset_password(
    request: PasswordResetConfirm,
    use_case: Annotated[ResetPasswordUseCase, Depends(get_reset_password_use_case)],
) -> dict[str, str]:
    """Reset password.

    Args:
        request: Password reset confirmation with token and new password
        use_case: Reset password use case

    Returns:
        Success message
    """
    await use_case.execute(request)
    return {"message": "Password has been reset successfully."}
