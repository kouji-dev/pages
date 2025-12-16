"""List backlog use case."""

from uuid import UUID

import structlog
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.backlog import BacklogListResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, ProjectRepository, SprintRepository
from src.infrastructure.database.models import IssueModel, SprintIssueModel

logger = structlog.get_logger()


class ListBacklogUseCase:
    """Use case for listing backlog issues."""

    def __init__(
        self,
        issue_repository: IssueRepository,
        sprint_repository: SprintRepository,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository
            sprint_repository: Sprint repository to find issues in sprints
            project_repository: Project repository to verify project exists
            session: Database session for queries
        """
        self._issue_repository = issue_repository
        self._sprint_repository = sprint_repository
        self._project_repository = project_repository
        self._session = session

    async def execute(
        self,
        project_id: UUID,
        page: int = 1,
        limit: int = 20,
        type_filter: str | None = None,
        assignee_id: UUID | None = None,
        priority_filter: str | None = None,
        sort_by: str = "backlog_order",  # backlog_order, created_at, updated_at, priority
    ) -> BacklogListResponse:
        """Execute backlog listing.

        Args:
            project_id: Project UUID
            page: Page number (1-indexed)
            limit: Number of items per page
            type_filter: Optional issue type filter
            assignee_id: Optional assignee filter
            priority_filter: Optional priority filter
            sort_by: Sort field (backlog_order, created_at, updated_at, priority)

        Returns:
            Paginated backlog list response

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info(
            "Listing backlog",
            project_id=str(project_id),
            page=page,
            limit=limit,
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        skip = (page - 1) * limit

        # Get all issue IDs that are in sprints
        sprint_issues_result = await self._session.execute(
            select(SprintIssueModel.issue_id).distinct()
        )
        sprint_issue_ids = {row[0] for row in sprint_issues_result.all()}

        # Build query for backlog issues (not in any sprint)
        query = select(IssueModel).where(
            IssueModel.project_id == project_id,
            IssueModel.deleted_at.is_(None),
        )

        # Exclude issues in sprints
        if sprint_issue_ids:
            query = query.where(~IssueModel.id.in_(sprint_issue_ids))

        # Apply filters
        if type_filter:
            query = query.where(IssueModel.type == type_filter)
        if assignee_id:
            query = query.where(IssueModel.assignee_id == assignee_id)
        if priority_filter:
            query = query.where(IssueModel.priority == priority_filter)

        # Apply sorting
        if sort_by == "backlog_order":
            query = query.order_by(
                IssueModel.backlog_order.asc().nulls_last(),
                IssueModel.created_at.asc(),
            )
        elif sort_by == "created_at":
            query = query.order_by(IssueModel.created_at.desc())
        elif sort_by == "updated_at":
            query = query.order_by(IssueModel.updated_at.desc())
        elif sort_by == "priority":
            # Priority order: critical > high > medium > low
            query = query.order_by(
                case(
                    (IssueModel.priority == "critical", 0),
                    (IssueModel.priority == "high", 1),
                    (IssueModel.priority == "medium", 2),
                    (IssueModel.priority == "low", 3),
                    else_=4,
                ).asc(),
                IssueModel.created_at.asc(),
            )
        else:
            # Default: backlog_order
            query = query.order_by(
                IssueModel.backlog_order.asc().nulls_last(),
                IssueModel.created_at.asc(),
            )

        # Get total count (before pagination)
        from sqlalchemy import func

        count_query = select(func.count(IssueModel.id)).where(
            IssueModel.project_id == project_id,
            IssueModel.deleted_at.is_(None),
        )

        if sprint_issue_ids:
            count_query = count_query.where(~IssueModel.id.in_(sprint_issue_ids))

        if type_filter:
            count_query = count_query.where(IssueModel.type == type_filter)
        if assignee_id:
            count_query = count_query.where(IssueModel.assignee_id == assignee_id)
        if priority_filter:
            count_query = count_query.where(IssueModel.priority == priority_filter)

        count_result = await self._session.execute(count_query)
        total = count_result.scalar_one() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        issues = result.scalars().all()

        issue_ids = [issue.id for issue in issues]

        # Calculate pages
        pages = (total + limit - 1) // limit if total > 0 else 0

        return BacklogListResponse(
            issues=issue_ids,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
