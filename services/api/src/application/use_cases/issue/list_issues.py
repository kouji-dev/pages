"""List issues use case."""

import math
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue import IssueListItemResponse, IssueListResponse
from src.domain.repositories import IssueRepository, ProjectRepository

logger = structlog.get_logger()


class ListIssuesUseCase:
    """Use case for listing issues with filters, search and pagination."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    def __init__(
        self,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository for data access
            project_repository: Project repository to get project keys for issue key generation
            session: Database session (for consistency, not directly used here)
        """
        self._issue_repository = issue_repository
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self,
        project_id: str,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
        search: str | None = None,
        assignee_id: str | None = None,
        reporter_id: str | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
        sprint_id: str | None = None,
    ) -> IssueListResponse:
        """Execute list issues.

        Args:
            project_id: Project ID to filter issues by
            page: Page number (1-based)
            limit: Number of issues per page
            search: Optional search query (title or description)
            assignee_id: Optional assignee filter
            reporter_id: Optional reporter filter
            status: Optional status filter
            type: Optional type filter
            priority: Optional priority filter

        Returns:
            Issue list response DTO with pagination metadata

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
            "Listing issues",
            project_id=project_id,
            page=page,
            limit=limit,
            search=search,
            assignee_id=assignee_id,
            reporter_id=reporter_id,
            status=status,
            type=type,
            priority=priority,
            sprint_id=sprint_id,
        )

        project_uuid = UUID(project_id)

        # Get project to generate issue keys
        project = await self._project_repository.get_by_id(project_uuid)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        # Convert filter IDs to UUIDs
        assignee_uuid = UUID(assignee_id) if assignee_id else None
        reporter_uuid = UUID(reporter_id) if reporter_id else None
        sprint_uuid = UUID(sprint_id) if sprint_id else None

        # Get issues based on filters
        if search:
            issues = await self._issue_repository.search(
                project_id=project_uuid, query=search, skip=skip, limit=limit
            )
            total = await self._issue_repository.count(
                project_id=project_uuid, include_deleted=False
            )  # Search only active issues
        else:
            issues = await self._issue_repository.get_all(
                project_id=project_uuid,
                skip=skip,
                limit=limit,
                include_deleted=False,
                assignee_id=assignee_uuid,
                reporter_id=reporter_uuid,
                status=status,
                type=type,
                priority=priority,
                sprint_id=sprint_uuid,
            )
            total = await self._issue_repository.count(
                project_id=project_uuid,
                include_deleted=False,
                assignee_id=assignee_uuid,
                reporter_id=reporter_uuid,
                status=status,
                type=type,
                priority=priority,
                sprint_id=sprint_uuid,
            )

        # Calculate total pages
        pages = math.ceil(total / limit) if total > 0 else 0

        # Convert to response DTOs with keys
        issue_responses = []
        for issue in issues:
            issue_key = issue.generate_key(project.key)
            issue_dict = {
                "id": issue.id,
                "project_id": issue.project_id,
                "issue_number": issue.issue_number,
                "key": issue_key,
                "title": issue.title,
                "type": issue.type,
                "status": issue.status,
                "priority": issue.priority,
                "assignee_id": issue.assignee_id,
                "reporter_id": issue.reporter_id,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
            }
            issue_responses.append(IssueListItemResponse.model_validate(issue_dict))

        logger.info(
            "Issues listed",
            count=len(issue_responses),
            total=total,
            pages=pages,
        )

        return IssueListResponse(
            issues=issue_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
