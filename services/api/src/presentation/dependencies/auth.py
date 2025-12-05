"""Authentication dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.interfaces import TokenService
from src.domain.entities import User
from src.domain.exceptions import AuthenticationException
from src.domain.repositories import UserRepository
from src.presentation.dependencies.services import get_token_service, get_user_repository

# HTTP Bearer scheme for JWT authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials
        token_service: Token service for JWT verification
        user_repository: User repository for fetching user

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = token_service.get_user_id_from_token(credentials.credentials)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.

    Ensures user is active and not deleted.

    Args:
        current_user: Current authenticated user

    Returns:
        Active user

    Raises:
        HTTPException: If user is inactive or deleted
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deleted",
        )

    return current_user


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User | None:
    """Get current user if authenticated, None otherwise.

    Use this for endpoints that work for both authenticated and anonymous users.

    Args:
        credentials: HTTP Bearer credentials (optional)
        token_service: Token service for JWT verification
        user_repository: User repository for fetching user

    Returns:
        User if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        user_id = token_service.get_user_id_from_token(credentials.credentials)
        return await user_repository.get_by_id(user_id)
    except AuthenticationException:
        return None


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
