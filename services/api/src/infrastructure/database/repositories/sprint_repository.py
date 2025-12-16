"""SQLAlchemy implementation of SprintRepository."""

from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Sprint
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import SprintRepository
from src.domain.value_objects.sprint_status import SprintStatus
from src.infrastructure.database.models import (
    IssueModel,
    SprintIssueModel,
    SprintModel,
)


class SQLAlchemySprintRepository(SprintRepository):
    """SQLAlchemy implementation of SprintRepository.

    Adapts the domain SprintRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, sprint: Sprint) -> Sprint:
        """Create a new sprint in the database.

        Args:
            sprint: Sprint domain entity

        Returns:
            Created sprint with persisted data
        """
        # Create model from entity
        model = SprintModel(
            id=sprint.id,
            project_id=sprint.project_id,
            name=sprint.name,
            goal=sprint.goal,
            start_date=sprint.start_date,
            end_date=sprint.end_date,
            status=str(sprint.status),
            created_at=sprint.created_at,
            updated_at=sprint.updated_at,
            deleted_at=sprint.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, sprint_id: UUID) -> Sprint | None:
        """Get sprint by ID.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Sprint if found, None otherwise (excludes soft-deleted sprints)
        """
        result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.id == sprint_id,
                SprintModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, sprint: Sprint) -> Sprint:
        """Update an existing sprint.

        Args:
            sprint: Sprint entity with updated data

        Returns:
            Updated sprint

        Raises:
            EntityNotFoundException: If sprint not found
        """
        result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.id == sprint.id,
                SprintModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Sprint", str(sprint.id))

        # Update model fields
        model.name = sprint.name
        model.goal = sprint.goal
        model.start_date = sprint.start_date
        model.end_date = sprint.end_date
        model.status = str(sprint.status)
        model.updated_at = sprint.updated_at
        model.deleted_at = sprint.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, sprint_id: UUID) -> None:
        """Hard delete a sprint.

        Args:
            sprint_id: Sprint UUID

        Raises:
            EntityNotFoundException: If sprint not found
        """
        result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.id == sprint_id,
                SprintModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Sprint", str(sprint_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_all(
        self,
        project_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: SprintStatus | None = None,
        include_deleted: bool = False,
    ) -> list[Sprint]:
        """Get all sprints in a project with filters and pagination.

        Args:
            project_id: Project UUID to filter by
            page: Page number (1-indexed)
            limit: Maximum number of records to return
            status: Optional status filter
            include_deleted: Whether to include soft-deleted sprints

        Returns:
            List of sprints
        """
        skip = (page - 1) * limit

        query = select(SprintModel).where(SprintModel.project_id == project_id)

        if not include_deleted:
            query = query.where(SprintModel.deleted_at.is_(None))

        if status:
            query = query.where(SprintModel.status == str(status))

        # Sort by start_date descending (most recent first)
        query = query.order_by(
            SprintModel.start_date.desc().nulls_last(),
            SprintModel.created_at.desc(),
        )

        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        project_id: UUID,
        status: SprintStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """Count total sprints in a project with filters.

        Args:
            project_id: Project UUID to filter by
            status: Optional status filter
            include_deleted: Whether to include soft-deleted sprints

        Returns:
            Total count of sprints
        """
        query = select(func.count(SprintModel.id)).where(SprintModel.project_id == project_id)

        if not include_deleted:
            query = query.where(SprintModel.deleted_at.is_(None))

        if status:
            query = query.where(SprintModel.status == str(status))

        result = await self._session.execute(query)
        return result.scalar_one() or 0

    async def find_overlapping_sprints(
        self,
        project_id: UUID,
        start_date: date,
        end_date: date,
        exclude_sprint_id: UUID | None = None,
    ) -> list[Sprint]:
        """Find sprints that overlap with the given date range.

        Args:
            project_id: Project UUID to filter by
            start_date: Start date of the date range
            end_date: End date of the date range
            exclude_sprint_id: Optional sprint ID to exclude from results

        Returns:
            List of overlapping sprints
        """
        query = select(SprintModel).where(
            SprintModel.project_id == project_id,
            SprintModel.deleted_at.is_(None),
            # Overlap condition: (start_date <= end_date) AND (end_date >= start_date)
            or_(
                # Sprint starts before or on the new end date
                and_(
                    SprintModel.start_date.isnot(None),
                    SprintModel.end_date.isnot(None),
                    SprintModel.start_date <= end_date,
                    SprintModel.end_date >= start_date,
                ),
                # Sprint has no dates (considered as overlapping for safety)
                and_(
                    SprintModel.start_date.is_(None),
                    SprintModel.end_date.is_(None),
                ),
            ),
        )

        if exclude_sprint_id:
            query = query.where(SprintModel.id != exclude_sprint_id)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_active_sprint(self, project_id: UUID) -> Sprint | None:
        """Get the active sprint for a project.

        Args:
            project_id: Project UUID

        Returns:
            Active sprint if found, None otherwise
        """
        result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.project_id == project_id,
                SprintModel.status == str(SprintStatus.ACTIVE),
                SprintModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def add_issue_to_sprint(
        self,
        sprint_id: UUID,
        issue_id: UUID,
        order: int,
    ) -> None:
        """Add an issue to a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID
            order: Order within the sprint

        Raises:
            EntityNotFoundException: If sprint or issue not found
            ConflictException: If issue is already in the sprint
        """
        # Check if sprint exists
        sprint_result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.id == sprint_id,
                SprintModel.deleted_at.is_(None),
            )
        )
        if sprint_result.scalar_one_or_none() is None:
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Check if issue exists
        issue_result = await self._session.execute(
            select(IssueModel).where(
                IssueModel.id == issue_id,
                IssueModel.deleted_at.is_(None),
            )
        )
        if issue_result.scalar_one_or_none() is None:
            raise EntityNotFoundException("Issue", str(issue_id))

        # Check if issue is already in the sprint
        existing_result = await self._session.execute(
            select(SprintIssueModel).where(
                SprintIssueModel.sprint_id == sprint_id,
                SprintIssueModel.issue_id == issue_id,
            )
        )
        if existing_result.scalar_one_or_none() is not None:
            raise ConflictException(f"Issue {issue_id} is already in sprint {sprint_id}")

        # Create sprint-issue relationship
        sprint_issue = SprintIssueModel(
            sprint_id=sprint_id,
            issue_id=issue_id,
            order=order,
        )

        self._session.add(sprint_issue)
        await self._session.flush()

    async def remove_issue_from_sprint(
        self,
        sprint_id: UUID,
        issue_id: UUID,
    ) -> None:
        """Remove an issue from a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID

        Raises:
            EntityNotFoundException: If sprint or issue not found
        """
        result = await self._session.execute(
            select(SprintIssueModel).where(
                SprintIssueModel.sprint_id == sprint_id,
                SprintIssueModel.issue_id == issue_id,
            )
        )
        sprint_issue = result.scalar_one_or_none()

        if sprint_issue is None:
            raise EntityNotFoundException("SprintIssue", f"{sprint_id}-{issue_id}")

        await self._session.delete(sprint_issue)
        await self._session.flush()

    async def reorder_sprint_issues(
        self,
        sprint_id: UUID,
        issue_orders: dict[UUID, int],
    ) -> None:
        """Reorder issues within a sprint.

        Args:
            sprint_id: Sprint UUID
            issue_orders: Dictionary mapping issue IDs to their new order

        Raises:
            EntityNotFoundException: If sprint not found
        """
        # Check if sprint exists
        sprint_result = await self._session.execute(
            select(SprintModel).where(
                SprintModel.id == sprint_id,
                SprintModel.deleted_at.is_(None),
            )
        )
        if sprint_result.scalar_one_or_none() is None:
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Update orders for each issue
        for issue_id, order in issue_orders.items():
            result = await self._session.execute(
                select(SprintIssueModel).where(
                    SprintIssueModel.sprint_id == sprint_id,
                    SprintIssueModel.issue_id == issue_id,
                )
            )
            sprint_issue = result.scalar_one_or_none()

            if sprint_issue:
                sprint_issue.order = order

        await self._session.flush()

    async def get_sprint_issues(
        self,
        sprint_id: UUID,
    ) -> list[tuple[UUID, int]]:
        """Get all issues in a sprint with their order.

        Args:
            sprint_id: Sprint UUID

        Returns:
            List of tuples (issue_id, order)
        """
        result = await self._session.execute(
            select(SprintIssueModel)
            .where(SprintIssueModel.sprint_id == sprint_id)
            .order_by(SprintIssueModel.order)
        )
        sprint_issues = result.scalars().all()

        return [(sprint_issue.issue_id, sprint_issue.order) for sprint_issue in sprint_issues]

    async def get_issue_sprint(self, issue_id: UUID) -> Sprint | None:
        """Get the sprint that contains an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            Sprint if found, None otherwise
        """
        result = await self._session.execute(
            select(SprintModel)
            .join(SprintIssueModel, SprintModel.id == SprintIssueModel.sprint_id)
            .where(
                SprintIssueModel.issue_id == issue_id,
                SprintModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: SprintModel) -> Sprint:
        """Convert SprintModel to Sprint domain entity.

        Args:
            model: SprintModel instance

        Returns:
            Sprint domain entity
        """
        from src.domain.value_objects.sprint_status import SprintStatus

        return Sprint(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            goal=model.goal,
            start_date=model.start_date,
            end_date=model.end_date,
            status=SprintStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
