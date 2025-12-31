"""List spaces use case."""

from math import ceil
from uuid import UUID

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.space import SpaceListItemResponse, SpaceListResponse
from src.application.dtos.user import UserDTO
from src.domain.repositories import SpaceRepository
from src.infrastructure.database.models import PageModel, SpaceModel, UserModel

logger = structlog.get_logger()


class ListSpacesUseCase:
    """Use case for listing spaces with pagination."""

    def __init__(
        self,
        space_repository: SpaceRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
            session: Database session for counting pages
        """
        self._space_repository = space_repository
        self._session = session

    async def execute(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
    ) -> SpaceListResponse:
        """Execute list spaces.

        Args:
            organization_id: Organization ID
            page: Page number (1-based)
            limit: Number of spaces per page
            search: Optional search query for name or key

        Returns:
            Space list response DTO with pagination metadata
        """
        org_uuid = UUID(organization_id)
        offset = (page - 1) * limit

        logger.info(
            "Listing spaces",
            organization_id=organization_id,
            page=page,
            limit=limit,
            search=search,
        )

        if search:
            spaces = await self._space_repository.search(
                organization_id=org_uuid, query=search, skip=offset, limit=limit
            )
            total = await self._count_search_results(org_uuid, search)
        else:
            spaces = await self._space_repository.get_all(
                organization_id=org_uuid, skip=offset, limit=limit
            )
            total = await self._space_repository.count(organization_id=org_uuid)

        # Calculate total pages
        pages = ceil(total / limit) if total > 0 else 0

        # Get page counts and owner for each space
        space_responses = []
        for space in spaces:
            # Count pages
            result = await self._session.execute(
                select(func.count())
                .select_from(PageModel)
                .where(PageModel.space_id == space.id, PageModel.deleted_at.is_(None))
            )
            page_count: int = result.scalar_one()

            # Get owner if created_by exists
            owner: UserDTO | None = None
            if space.created_by:
                owner_result = await self._session.execute(
                    select(UserModel).where(UserModel.id == space.created_by)
                )
                owner_user = owner_result.scalar_one_or_none()
                if owner_user:
                    owner = UserDTO(
                        id=owner_user.id,
                        name=owner_user.name,
                        email=owner_user.email,
                        avatar_url=owner_user.avatar_url,
                    )

            space_responses.append(
                SpaceListItemResponse(
                    id=space.id,
                    organization_id=space.organization_id,
                    name=space.name,
                    key=space.key,
                    description=space.description,
                    deleted_at=space.deleted_at,
                    icon=space.icon,
                    status=space.status,
                    view_count=space.view_count,
                    page_count=page_count,
                    owner=owner,
                    created_at=space.created_at,
                    updated_at=space.updated_at,
                )
            )

        logger.info("Spaces listed", count=len(space_responses), total=total, pages=pages)

        return SpaceListResponse(
            spaces=space_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def _count_search_results(self, organization_id: UUID, query: str) -> int:
        """Count search results.

        Args:
            organization_id: Organization UUID
            query: Search query

        Returns:
            Total count of matching spaces
        """
        search_pattern = f"%{query}%"

        stmt = (
            select(func.count())
            .select_from(SpaceModel)
            .where(
                SpaceModel.organization_id == organization_id,
                SpaceModel.deleted_at.is_(None),
                or_(
                    SpaceModel.name.ilike(search_pattern),
                    SpaceModel.key.ilike(search_pattern),
                ),
            )
        )

        result = await self._session.execute(stmt)
        count: int = result.scalar_one()
        return count
