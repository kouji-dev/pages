"""List issue activities use case."""

import math
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue_activity import (
    IssueActivityListResponse,
    IssueActivityResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueActivityRepository, IssueRepository
from src.infrastructure.database.models import IssueActivityModel, UserModel

logger = structlog.get_logger()


class ListIssueActivitiesUseCase:
    """Use case for listing activities for an issue."""

    def __init__(
        self,
        issue_repository: IssueRepository,
        activity_repository: IssueActivityRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository to verify issue exists
            activity_repository: Issue activity repository
            session: Database session for loading user details
        """
        self._issue_repository = issue_repository
        self._activity_repository = activity_repository
        self._session = session

    async def execute(
        self, issue_id: str, page: int = 1, limit: int = 50
    ) -> IssueActivityListResponse:
        """Execute list activities for issue.

        Args:
            issue_id: Issue ID
            page: Page number (1-based)
            limit: Number of items per page

        Returns:
            List of activities response DTO

        Raises:
            EntityNotFoundException: If issue not found
        """
        logger.info("Listing activities for issue", issue_id=issue_id, page=page, limit=limit)

        # Verify issue exists
        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)
        if issue is None:
            logger.warning("Issue not found", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Calculate pagination
        skip = (page - 1) * limit

        # Get activities
        activities = await self._activity_repository.get_by_issue_id(
            issue_uuid, skip=skip, limit=limit
        )
        total = await self._activity_repository.count_by_issue_id(issue_uuid)

        # Load user details for activities
        user_ids = {activity.user_id for activity in activities if activity.user_id}
        users_map = {}
        if user_ids:
            result = await self._session.execute(
                select(UserModel).where(UserModel.id.in_(user_ids))
            )
            users = result.scalars().all()
            users_map = {user.id: user for user in users}

        # Convert to response DTOs
        activity_responses = []
        for activity in activities:
            user = users_map.get(activity.user_id) if activity.user_id else None
            activity_responses.append(
                IssueActivityResponse(
                    id=activity.id,
                    issue_id=activity.issue_id,
                    user_id=activity.user_id,
                    action=activity.action,
                    field_name=activity.field_name,
                    old_value=activity.old_value,
                    new_value=activity.new_value,
                    user_name=user.name if user else None,
                    user_email=user.email if user else None,
                    created_at=activity.created_at,
                )
            )

        total_pages = math.ceil(total / limit) if total > 0 else 0

        logger.info(
            "Activities listed successfully",
            issue_id=issue_id,
            total=total,
            page=page,
            limit=limit,
        )

        return IssueActivityListResponse(
            activities=activity_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

