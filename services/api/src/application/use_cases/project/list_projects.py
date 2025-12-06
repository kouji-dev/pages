"""List projects use case."""

from math import ceil
from uuid import UUID

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.project import ProjectListItemResponse, ProjectListResponse
from src.domain.repositories import ProjectRepository
from src.infrastructure.database.models import IssueModel, ProjectMemberModel

logger = structlog.get_logger()


class ListProjectsUseCase:
    """Use case for listing projects with pagination."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            project_repository: Project repository
            session: Database session for counting members and issues
        """
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
    ) -> ProjectListResponse:
        """Execute list projects.

        Args:
            organization_id: Organization ID
            page: Page number (1-based)
            limit: Number of projects per page
            search: Optional search query for name or key

        Returns:
            Project list response DTO with pagination metadata
        """
        org_uuid = UUID(organization_id)
        offset = (page - 1) * limit

        logger.info(
            "Listing projects",
            organization_id=organization_id,
            page=page,
            limit=limit,
            search=search,
        )

        if search:
            projects = await self._project_repository.search(
                organization_id=org_uuid, query=search, skip=offset, limit=limit
            )
            total = await self._count_search_results(org_uuid, search)
        else:
            projects = await self._project_repository.get_all(
                organization_id=org_uuid, skip=offset, limit=limit
            )
            total = await self._project_repository.count(organization_id=org_uuid)

        # Calculate total pages
        pages = ceil(total / limit) if total > 0 else 0

        # Get member and issue counts for each project
        project_responses = []
        for project in projects:
            # Count members
            result = await self._session.execute(
                select(func.count())
                .select_from(ProjectMemberModel)
                .where(ProjectMemberModel.project_id == project.id)
            )
            member_count: int = result.scalar_one()

            # Count issues
            result = await self._session.execute(
                select(func.count())
                .select_from(IssueModel)
                .where(IssueModel.project_id == project.id)
            )
            issue_count: int = result.scalar_one()

            project_responses.append(
                ProjectListItemResponse(
                    id=project.id,
                    organization_id=project.organization_id,
                    name=project.name,
                    key=project.key,
                    description=project.description,
                    member_count=member_count,
                    issue_count=issue_count,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                )
            )

        logger.info("Projects listed", count=len(project_responses), total=total, pages=pages)

        return ProjectListResponse(
            projects=project_responses,
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
            Total count of matching projects
        """
        from src.infrastructure.database.models import ProjectModel

        search_pattern = f"%{query}%"

        stmt = (
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.organization_id == organization_id,
                ProjectModel.deleted_at.is_(None),
                or_(
                    ProjectModel.name.ilike(search_pattern),
                    ProjectModel.key.ilike(search_pattern),
                ),
            )
        )

        result = await self._session.execute(stmt)
        count: int = result.scalar_one()
        return count
