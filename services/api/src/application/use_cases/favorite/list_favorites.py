"""List favorites use case."""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.favorite import FavoriteListItemResponse, FavoriteListResponse
from src.application.dtos.node import NodeDetailsProject, NodeDetailsSpace, NodeListItemResponse
from src.domain.repositories import FavoriteRepository, ProjectRepository, SpaceRepository
from src.domain.value_objects.entity_type import EntityType
from src.infrastructure.database.models import (
    IssueModel,
    PageModel,
    ProjectMemberModel,
    ProjectModel,
    SpaceModel,
)

logger = structlog.get_logger()


class ListFavoritesUseCase:
    """Use case for listing favorites for a user."""

    def __init__(
        self,
        favorite_repository: FavoriteRepository,
        project_repository: ProjectRepository,
        space_repository: SpaceRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            favorite_repository: Favorite repository
            project_repository: Project repository
            space_repository: Space repository
            session: Database session for getting folder_id and counts
        """
        self._favorite_repository = favorite_repository
        self._project_repository = project_repository
        self._space_repository = space_repository
        self._session = session

    async def execute(
        self,
        user_id: str,
        entity_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> FavoriteListResponse:
        """Execute list favorites.

        Args:
            user_id: User UUID
            entity_type: Optional entity type to filter by (project or space only)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Favorite list response DTO
        """
        user_uuid = UUID(user_id)
        entity_type_vo = EntityType.from_string(entity_type) if entity_type else None

        logger.info(
            "Listing favorites",
            user_id=user_id,
            entity_type=entity_type,
            skip=skip,
            limit=limit,
        )

        favorites = await self._favorite_repository.get_all(
            user_id=user_uuid,
            entity_type=entity_type_vo,
            skip=skip,
            limit=limit,
        )

        total = await self._favorite_repository.count(
            user_id=user_uuid,
            entity_type=entity_type_vo,
        )

        favorite_responses = []

        for favorite in favorites:
            # Favorites are only allowed for projects and spaces
            # Skip any favorites that are not projects or spaces (shouldn't happen, but safety check)
            if not favorite.entity_type.is_project() and not favorite.entity_type.is_space():
                logger.warning(
                    "Skipping favorite with unsupported entity type",
                    favorite_id=str(favorite.id),
                    entity_type=favorite.entity_type.value,
                )
                continue

            node_data: NodeListItemResponse | None = None

            # Enrich with node data for projects and spaces only (no folders)
            if favorite.entity_type.is_project():
                project = await self._project_repository.get_by_id(favorite.entity_id)
                if project:
                    # Get folder_id from model
                    folder_result = await self._session.execute(
                        select(ProjectModel.folder_id).where(ProjectModel.id == project.id)
                    )
                    project_folder_id = folder_result.scalar_one_or_none()

                    # Count members
                    member_result = await self._session.execute(
                        select(func.count())
                        .select_from(ProjectMemberModel)
                        .where(ProjectMemberModel.project_id == project.id)
                    )
                    member_count: int = member_result.scalar_one()

                    # Count issues
                    issue_result = await self._session.execute(
                        select(func.count())
                        .select_from(IssueModel)
                        .where(IssueModel.project_id == project.id)
                    )
                    issue_count: int = issue_result.scalar_one()

                    node_data = NodeListItemResponse(
                        type="project",
                        id=project.id,
                        organization_id=project.organization_id,
                        details=NodeDetailsProject(
                            name=project.name,
                            key=project.key,
                            description=project.description,
                            folder_id=project_folder_id,
                            member_count=member_count,
                            issue_count=issue_count,
                        ),
                    )

            elif favorite.entity_type.is_space():
                space = await self._space_repository.get_by_id(favorite.entity_id)
                if space:
                    # Get folder_id from model
                    space_folder_result = await self._session.execute(
                        select(SpaceModel.folder_id).where(SpaceModel.id == space.id)
                    )
                    space_folder_id = space_folder_result.scalar_one_or_none()

                    # Count pages
                    page_count_result = await self._session.execute(
                        select(func.count())
                        .select_from(PageModel)
                        .where(PageModel.space_id == space.id)
                    )
                    page_count: int = page_count_result.scalar_one()

                    node_data = NodeListItemResponse(
                        type="space",
                        id=space.id,
                        organization_id=space.organization_id,
                        details=NodeDetailsSpace(
                            name=space.name,
                            key=space.key,
                            description=space.description,
                            folder_id=space_folder_id,
                            page_count=page_count,
                        ),
                    )

            # If node_data is None, skip this favorite (entity not found)
            if node_data is None:
                logger.warning(
                    "Skipping favorite - entity not found",
                    favorite_id=str(favorite.id),
                    entity_type=favorite.entity_type.value,
                    entity_id=str(favorite.entity_id),
                )
                continue

            favorite_responses.append(
                FavoriteListItemResponse(
                    id=favorite.id,
                    user_id=favorite.user_id,
                    entity_type=favorite.entity_type.value,
                    entity_id=favorite.entity_id,
                    created_at=favorite.created_at,
                    updated_at=favorite.updated_at,
                    node=node_data,
                )
            )

        logger.info("Favorites listed", count=len(favorite_responses), total=total)

        return FavoriteListResponse(favorites=favorite_responses, total=total)
