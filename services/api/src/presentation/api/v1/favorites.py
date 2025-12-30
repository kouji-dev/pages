"""Favorite management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.favorite import (
    CreateFavoriteRequest,
    FavoriteListResponse,
    FavoriteResponse,
)
from src.application.use_cases.favorite import (
    CreateFavoriteUseCase,
    DeleteFavoriteUseCase,
    ListFavoritesUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    FavoriteRepository,
    ProjectRepository,
    SpaceRepository,
    UserRepository,
)
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import (
    get_favorite_repository,
    get_project_repository,
    get_space_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_favorite_use_case(
    favorite_repository: Annotated[FavoriteRepository, Depends(get_favorite_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> CreateFavoriteUseCase:
    """Get create favorite use case with dependencies."""
    return CreateFavoriteUseCase(favorite_repository, user_repository)


def get_list_favorites_use_case(
    favorite_repository: Annotated[FavoriteRepository, Depends(get_favorite_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListFavoritesUseCase:
    """Get list favorites use case with dependencies."""
    return ListFavoritesUseCase(favorite_repository, project_repository, space_repository, session)


def get_delete_favorite_use_case(
    favorite_repository: Annotated[FavoriteRepository, Depends(get_favorite_repository)],
) -> DeleteFavoriteUseCase:
    """Get delete favorite use case with dependencies."""
    return DeleteFavoriteUseCase(favorite_repository)


@router.get(
    "/users/me/favorites",
    response_model=FavoriteListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_favorites(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListFavoritesUseCase, Depends(get_list_favorites_use_case)],
    entity_type: str | None = Query(
        None, description="Filter by entity type (project, space, page)"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> FavoriteListResponse:
    """List favorites for the current user.

    Args:
        current_user: Current authenticated user
        use_case: List favorites use case
        entity_type: Optional entity type to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Favorite list response
    """
    return await use_case.execute(
        user_id=str(current_user.id),
        entity_type=entity_type,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/users/me/favorites",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_favorite(
    request: CreateFavoriteRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreateFavoriteUseCase, Depends(get_create_favorite_use_case)],
) -> FavoriteResponse:
    """Add a favorite for the current user.

    Args:
        request: Favorite creation request
        current_user: Current authenticated user
        use_case: Create favorite use case

    Returns:
        Created favorite response

    Raises:
        HTTPException: If favorite already exists or entity not found
    """
    return await use_case.execute(request, str(current_user.id))


@router.delete(
    "/users/me/favorites/{favorite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_favorite(
    favorite_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteFavoriteUseCase, Depends(get_delete_favorite_use_case)],
) -> None:
    """Remove a favorite for the current user.

    Args:
        favorite_id: Favorite UUID (from path)
        current_user: Current authenticated user
        use_case: Delete favorite use case

    Raises:
        HTTPException: If favorite not found
    """
    await use_case.execute(str(favorite_id))
