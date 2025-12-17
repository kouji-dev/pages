"""Service dependencies for FastAPI dependency injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import TokenService
from src.application.services.permission_service import DatabasePermissionService
from src.application.services.search_query_service import SearchQueryService
from src.domain.repositories import (
    AttachmentRepository,
    CommentRepository,
    InvitationRepository,
    IssueActivityRepository,
    IssueRepository,
    NotificationRepository,
    OrganizationRepository,
    PageRepository,
    ProjectRepository,
    SpaceRepository,
    SprintRepository,
    TemplateRepository,
    UserRepository,
    WorkflowRepository,
)
from src.domain.repositories.custom_field_repository import CustomFieldRepository
from src.domain.repositories.dashboard_repository import DashboardRepository
from src.domain.repositories.issue_link_repository import IssueLinkRepository
from src.domain.repositories.saved_filter_repository import SavedFilterRepository
from src.domain.repositories.time_entry_repository import TimeEntryRepository
from src.domain.services import PasswordService, PermissionService, StorageService
from src.infrastructure.database import get_session
from src.infrastructure.database.repositories import (
    SQLAlchemyAttachmentRepository,
    SQLAlchemyCommentRepository,
    SQLAlchemyCustomFieldRepository,
    SQLAlchemyDashboardRepository,
    SQLAlchemyInvitationRepository,
    SQLAlchemyIssueActivityRepository,
    SQLAlchemyIssueLinkRepository,
    SQLAlchemyIssueRepository,
    SQLAlchemyNotificationRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyPageRepository,
    SQLAlchemyProjectRepository,
    SQLAlchemySavedFilterRepository,
    SQLAlchemySpaceRepository,
    SQLAlchemySprintRepository,
    SQLAlchemyTemplateRepository,
    SQLAlchemyTimeEntryRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyWorkflowRepository,
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


async def get_invitation_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InvitationRepository:
    """Get invitation repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of InvitationRepository
    """
    return SQLAlchemyInvitationRepository(session)


async def get_project_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectRepository:
    """Get project repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of ProjectRepository
    """
    return SQLAlchemyProjectRepository(session)


async def get_issue_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IssueRepository:
    """Get issue repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of IssueRepository
    """
    return SQLAlchemyIssueRepository(session)


async def get_issue_activity_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IssueActivityRepository:
    """Get issue activity repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of IssueActivityRepository
    """
    return SQLAlchemyIssueActivityRepository(session)


async def get_comment_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CommentRepository:
    """Get comment repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of CommentRepository
    """
    return SQLAlchemyCommentRepository(session)


async def get_attachment_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AttachmentRepository:
    """Get attachment repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of AttachmentRepository
    """
    return SQLAlchemyAttachmentRepository(session)


async def get_space_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SpaceRepository:
    """Get space repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of SpaceRepository
    """
    return SQLAlchemySpaceRepository(session)


async def get_page_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PageRepository:
    """Get page repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of PageRepository
    """
    return SQLAlchemyPageRepository(session)


async def get_template_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TemplateRepository:
    """Get template repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of TemplateRepository
    """
    return SQLAlchemyTemplateRepository(session)


async def get_notification_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationRepository:
    """Get notification repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of NotificationRepository
    """
    return SQLAlchemyNotificationRepository(session)


async def get_sprint_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SprintRepository:
    """Get sprint repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of SprintRepository
    """
    return SQLAlchemySprintRepository(session)


async def get_workflow_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WorkflowRepository:
    """Get workflow repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of WorkflowRepository
    """
    return SQLAlchemyWorkflowRepository(session)


async def get_custom_field_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CustomFieldRepository:
    """Get custom field repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of CustomFieldRepository
    """
    return SQLAlchemyCustomFieldRepository(session)


async def get_time_entry_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TimeEntryRepository:
    """Get time entry repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of TimeEntryRepository
    """
    return SQLAlchemyTimeEntryRepository(session)


async def get_issue_link_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IssueLinkRepository:
    """Get issue link repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of IssueLinkRepository
    """
    return SQLAlchemyIssueLinkRepository(session)


async def get_dashboard_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DashboardRepository:
    """Get dashboard repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of DashboardRepository
    """
    return SQLAlchemyDashboardRepository(session)


async def get_saved_filter_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SavedFilterRepository:
    """Get saved filter repository instance with database session.

    Args:
        session: Async database session from dependency injection

    Returns:
        SQLAlchemy implementation of SavedFilterRepository
    """
    return SQLAlchemySavedFilterRepository(session)


async def get_search_query_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchQueryService:
    """Get search query service (issues/pages)."""

    return SearchQueryService(session)


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
