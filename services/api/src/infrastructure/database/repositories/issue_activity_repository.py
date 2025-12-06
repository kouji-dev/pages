"""SQLAlchemy implementation of IssueActivityRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.issue_activity_repository import IssueActivityRepository
from src.infrastructure.database.models import IssueActivityModel


class SQLAlchemyIssueActivityRepository(IssueActivityRepository):
    """SQLAlchemy implementation of IssueActivityRepository.

    Adapts the domain IssueActivityRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(
        self,
        issue_id: UUID,
        user_id: UUID | None,
        action: str,
        field_name: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> IssueActivityModel:
        """Create a new activity log entry.

        Args:
            issue_id: Issue UUID
            user_id: User UUID who performed the action
            action: Action type
            field_name: Optional field name that was changed
            old_value: Optional old value
            new_value: Optional new value

        Returns:
            Created activity model
        """
        activity = IssueActivityModel(
            issue_id=issue_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
        )
        self._session.add(activity)
        await self._session.flush()
        await self._session.refresh(activity)
        return activity

    async def get_by_issue_id(
        self,
        issue_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[IssueActivityModel]:
        """Get all activities for an issue.

        Args:
            issue_id: Issue UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of activity models, ordered by created_at DESC
        """
        result = await self._session.execute(
            select(IssueActivityModel)
            .where(IssueActivityModel.issue_id == issue_id)
            .order_by(IssueActivityModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_issue_id(self, issue_id: UUID) -> int:
        """Count total activities for an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            Total count of activities
        """
        result = await self._session.execute(
            select(func.count(IssueActivityModel.id)).where(IssueActivityModel.issue_id == issue_id)
        )
        return result.scalar_one() or 0
