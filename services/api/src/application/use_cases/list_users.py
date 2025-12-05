"""User list use case."""

import math
from uuid import UUID

import structlog

from src.application.dtos.user import UserListResponse, UserResponse
from src.domain.repositories import UserRepository

logger = structlog.get_logger()


class ListUsersUseCase:
    """Use case for listing users with search and filters."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
        """
        self._user_repository = user_repository

    async def execute(
        self,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        search: str | None = None,
        organization_id: str | None = None,
    ) -> UserListResponse:
        """Execute list users.

        Args:
            page: Page number (1-based)
            limit: Number of users per page
            search: Optional search query (name or email)
            organization_id: Optional organization ID to filter by

        Returns:
            User list response DTO with pagination metadata

        Raises:
            ValueError: If page or limit is invalid
        """
        # Validate pagination
        if page < 1:
            raise ValueError("Page must be >= 1")

        if limit < 1:
            raise ValueError("Limit must be >= 1")

        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT

        # Calculate skip
        skip = (page - 1) * limit

        logger.info(
            "Listing users",
            page=page,
            limit=limit,
            search=search,
            organization_id=organization_id,
        )

        # Get users based on filters
        if search:
            # Use search method (case-insensitive search on name/email)
            users = await self._user_repository.search(query=search, skip=skip, limit=limit)
            # Count total matching users
            total = await self._count_search_results(search)
        elif organization_id:
            # Filter by organization
            org_uuid = UUID(organization_id)
            users = await self._get_users_by_organization(org_uuid, skip=skip, limit=limit)
            total = await self._count_users_by_organization(org_uuid)
        else:
            # Get all users with pagination
            users = await self._user_repository.get_all(
                skip=skip, limit=limit, include_deleted=False
            )
            total = await self._user_repository.count(include_deleted=False)

        # Calculate total pages
        pages = math.ceil(total / limit) if total > 0 else 0

        # Convert to response DTOs
        user_responses = [
            UserResponse(
                id=user.id,
                email=user.email.value,
                name=user.name,
                avatar_url=user.avatar_url,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]

        logger.info("Users listed", count=len(user_responses), total=total, pages=pages)

        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def _get_users_by_organization(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list:
        """Get users by organization membership.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users in the organization
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from src.infrastructure.database.models import OrganizationMemberModel, UserModel

        # Access the session from repository (not ideal, but needed for custom query)
        # Better approach would be to add this method to the repository interface
        session = self._user_repository._session

        stmt = (
            select(UserModel)
            .join(OrganizationMemberModel, UserModel.id == OrganizationMemberModel.user_id)
            .where(
                OrganizationMemberModel.organization_id == organization_id,
                UserModel.deleted_at.is_(None),
            )
            .options(selectinload(UserModel.organization_memberships))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.name)
        )

        result = await session.execute(stmt)
        models = result.scalars().all()

        return [self._user_repository._to_entity(model) for model in models]

    async def _count_users_by_organization(self, organization_id: UUID) -> int:
        """Count users in organization.

        Args:
            organization_id: Organization UUID

        Returns:
            Total count of users in the organization
        """
        from sqlalchemy import func, select

        from src.infrastructure.database.models import OrganizationMemberModel, UserModel

        session = self._user_repository._session

        stmt = (
            select(func.count())
            .select_from(UserModel)
            .join(OrganizationMemberModel, UserModel.id == OrganizationMemberModel.user_id)
            .where(
                OrganizationMemberModel.organization_id == organization_id,
                UserModel.deleted_at.is_(None),
            )
        )

        result = await session.execute(stmt)
        count: int = result.scalar_one()
        return count

    async def _count_search_results(self, query: str) -> int:
        """Count search results.

        Args:
            query: Search query

        Returns:
            Total count of matching users
        """
        from sqlalchemy import func, or_, select

        from src.infrastructure.database.models import UserModel

        session = self._user_repository._session
        search_pattern = f"%{query}%"

        stmt = (
            select(func.count())
            .select_from(UserModel)
            .where(
                UserModel.deleted_at.is_(None),
                or_(
                    UserModel.name.ilike(search_pattern),
                    UserModel.email.ilike(search_pattern),
                ),
            )
        )

        result = await session.execute(stmt)
        count: int = result.scalar_one()
        return count
