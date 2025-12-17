"""SQLAlchemy implementation of IssueRepository."""

from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Issue
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository
from src.infrastructure.database.models import IssueModel, ProjectModel


class SQLAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy implementation of IssueRepository.

    Adapts the domain IssueRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def get_next_issue_number(self, project_id: UUID) -> int:
        """Get the next issue number for a project.

        This uses an advisory lock to ensure atomicity and prevent duplicates.

        Args:
            project_id: Project UUID

        Returns:
            Next issue number (starting from 1)
        """
        # Use PostgreSQL advisory lock to ensure atomicity
        # Convert project_id to int for advisory lock (using hash)
        lock_id = hash(str(project_id)) % (2**31)  # PostgreSQL advisory lock range

        # Acquire advisory lock (transaction-level, automatically released on commit/rollback)
        await self._session.execute(text(f"SELECT pg_advisory_xact_lock({lock_id})"))

        # Get the maximum issue number for this project
        result = await self._session.execute(
            select(func.coalesce(func.max(IssueModel.issue_number), 0))
            .select_from(IssueModel)
            .where(IssueModel.project_id == project_id)
        )
        max_number: int = result.scalar_one() or 0

        # Return next number (max + 1)
        return max_number + 1

    async def create(self, issue: Issue) -> Issue:
        """Create a new issue in the database.

        Args:
            issue: Issue domain entity

        Returns:
            Created issue with persisted data
        """
        # Create model from entity
        model = IssueModel(
            id=issue.id,
            project_id=issue.project_id,
            issue_number=issue.issue_number,
            title=issue.title,
            description=issue.description,
            type=issue.type,
            status=issue.status,
            priority=issue.priority,
            reporter_id=issue.reporter_id,
            assignee_id=issue.assignee_id,
            parent_issue_id=issue.parent_issue_id,
            due_date=issue.due_date,
            story_points=issue.story_points,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            deleted_at=issue.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, issue_id: UUID) -> Issue | None:
        """Get issue by ID.

        Args:
            issue_id: Issue UUID

        Returns:
            Issue if found, None otherwise (excludes soft-deleted issues)
        """
        result = await self._session.execute(
            select(IssueModel).where(
                IssueModel.id == issue_id,
                IssueModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_key(self, project_key: str, issue_number: int) -> Issue | None:
        """Get issue by project key and issue number.

        Args:
            project_key: Project key (e.g., "PROJ")
            issue_number: Issue number (e.g., 123)

        Returns:
            Issue if found, None otherwise
        """
        # Join with ProjectModel to get project by key
        result = await self._session.execute(
            select(IssueModel)
            .join(ProjectModel, IssueModel.project_id == ProjectModel.id)
            .where(ProjectModel.key == project_key, IssueModel.issue_number == issue_number)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, issue: Issue) -> Issue:
        """Update an existing issue.

        Args:
            issue: Issue entity with updated data

        Returns:
            Updated issue

        Raises:
            EntityNotFoundException: If issue not found
        """
        result = await self._session.execute(select(IssueModel).where(IssueModel.id == issue.id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Issue", str(issue.id))

        # Update model fields
        model.title = issue.title
        model.description = issue.description
        model.type = issue.type
        model.status = issue.status
        model.priority = issue.priority
        model.reporter_id = issue.reporter_id
        model.assignee_id = issue.assignee_id
        model.due_date = issue.due_date
        model.story_points = issue.story_points
        model.updated_at = issue.updated_at
        model.deleted_at = issue.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, issue_id: UUID) -> None:
        """Hard delete an issue.

        Args:
            issue_id: Issue UUID

        Raises:
            EntityNotFoundException: If issue not found
        """
        result = await self._session.execute(select(IssueModel).where(IssueModel.id == issue_id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("Issue", str(issue_id))

        await self._session.delete(model)
        await self._session.flush()

    async def get_all(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
    ) -> list[Issue]:
        """Get all issues in a project with filters and pagination.

        Args:
            project_id: Project UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted issues
            assignee_id: Optional assignee filter
            reporter_id: Optional reporter filter
            status: Optional status filter
            type: Optional type filter
            priority: Optional priority filter

        Returns:
            List of issues
        """
        query = select(IssueModel).where(IssueModel.project_id == project_id)

        if not include_deleted:
            query = query.where(IssueModel.deleted_at.is_(None))

        if assignee_id:
            query = query.where(IssueModel.assignee_id == assignee_id)

        if reporter_id:
            query = query.where(IssueModel.reporter_id == reporter_id)

        if status:
            query = query.where(IssueModel.status == status)

        if type:
            query = query.where(IssueModel.type == type)

        if priority:
            query = query.where(IssueModel.priority == priority)

        query = query.offset(skip).limit(limit).order_by(IssueModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(
        self,
        project_id: UUID,
        include_deleted: bool = False,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: str | None = None,
        type: str | None = None,
        priority: str | None = None,
    ) -> int:
        """Count total issues in a project with filters.

        Args:
            project_id: Project UUID to filter by
            include_deleted: Whether to include soft-deleted issues
            assignee_id: Optional assignee filter
            reporter_id: Optional reporter filter
            status: Optional status filter
            type: Optional type filter
            priority: Optional priority filter

        Returns:
            Total count of issues
        """
        query = (
            select(func.count()).select_from(IssueModel).where(IssueModel.project_id == project_id)
        )

        if not include_deleted:
            query = query.where(IssueModel.deleted_at.is_(None))

        if assignee_id:
            query = query.where(IssueModel.assignee_id == assignee_id)

        if reporter_id:
            query = query.where(IssueModel.reporter_id == reporter_id)

        if status:
            query = query.where(IssueModel.status == status)

        if type:
            query = query.where(IssueModel.type == type)

        if priority:
            query = query.where(IssueModel.priority == priority)

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        project_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Issue]:
        """Search issues by title or description within a project.

        Args:
            project_id: Project UUID to filter by
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching issues
        """
        search_pattern = f"%{query}%"

        stmt = select(IssueModel).where(
            IssueModel.project_id == project_id,
            IssueModel.deleted_at.is_(None),
            or_(
                IssueModel.title.ilike(search_pattern),
                IssueModel.description.ilike(search_pattern),
            ),
        )

        stmt = stmt.offset(skip).limit(limit).order_by(IssueModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: IssueModel) -> Issue:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy IssueModel

        Returns:
            Issue domain entity
        """
        return Issue(
            id=model.id,
            project_id=model.project_id,
            issue_number=model.issue_number,
            title=model.title,
            description=model.description,
            type=model.type,
            status=model.status,
            priority=model.priority,
            reporter_id=model.reporter_id,
            assignee_id=model.assignee_id,
            parent_issue_id=model.parent_issue_id,
            due_date=model.due_date,
            story_points=model.story_points,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
