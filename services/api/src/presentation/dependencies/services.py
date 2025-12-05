"""Service dependencies for FastAPI dependency injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import TokenService
from src.application.services.permission_service import DatabasePermissionService
from src.domain.repositories import OrganizationRepository, UserRepository
from src.domain.services import PasswordService, PermissionService, StorageService
from src.infrastructure.database import get_session
from src.infrastructure.database.repositories import (
    SQLAlchemyOrganizationRepository,
    SQLAlchemyUserRepository,
)
from src.infrastructure.security import BcryptPasswordService, JWTTokenService
from src.infrastructure.services.local_storage_service import LocalStorageService


@lru_cache
def get_password_service() -> PasswordService:
    """Get password service instance (singleton)."""
    return BcryptPasswordService()


@lru_cache
def get_token_service() -> TokenService:
    """Get token service instance (singleton)."""
    return JWTTokenService()


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Get user repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of UserRepository
    """
    return SQLAlchemyUserRepository(session)


async def get_organization_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationRepository:
    """Get organization repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of OrganizationRepository
    """
    return SQLAlchemyOrganizationRepository(session)


async def get_permission_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PermissionService:
    """Get permission service instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        DatabasePermissionService instance
    """
    return DatabasePermissionService(session)


@lru_cache
def get_storage_service() -> StorageService:
    """Get storage service instance (singleton).

    Returns:
        LocalStorageService instance
    """
    return LocalStorageService()
