"""Real-time collaboration API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.dtos.presence import (
    PresenceListResponse,
    PresenceResponse,
)
from src.application.services.collaboration_service import CollaborationService
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PageRepository,
    PresenceRepository,
    SpaceRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_page_repository,
    get_permission_service,
    get_presence_repository,
    get_space_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for collaboration service
def get_collaboration_service(
    presence_repository: Annotated[PresenceRepository, Depends(get_presence_repository)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> CollaborationService:
    """Get collaboration service with dependencies."""
    return CollaborationService(presence_repository, page_repository, user_repository)


@router.get(
    "/pages/{page_id}/presence",
    response_model=PresenceListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_page_presence(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    collaboration_service: Annotated[CollaborationService, Depends(get_collaboration_service)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> PresenceListResponse:
    """Get active presences for a page.

    Returns list of users currently viewing/editing the page.

    Args:
        page_id: Page UUID (from path)
        current_user: Current authenticated user
        collaboration_service: Collaboration service
        page_repository: Page repository
        space_repository: Space repository
        permission_service: Permission service

    Returns:
        Presence list response

    Raises:
        HTTPException: If page not found or user lacks permission
    """
    page = await page_repository.get_by_id(page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    presences = await collaboration_service.get_page_presences(page_id)

    presence_responses = [
        PresenceResponse(
            id=p.id,
            page_id=p.page_id,
            user_id=p.user_id,
            cursor_position=p.cursor_position,
            selection=p.selection,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in presences
    ]

    return PresenceListResponse(
        presences=presence_responses,
        total=len(presence_responses),
    )
