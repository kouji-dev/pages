"""Update issue use case."""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue import IssueResponse, UpdateIssueRequest
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import (
    IssueActivityRepository,
    IssueRepository,
    ProjectRepository,
    UserRepository,
)

logger = structlog.get_logger()


class UpdateIssueUseCase:
    """Use case for updating an issue."""

    def __init__(
        self,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        activity_repository: IssueActivityRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository for data access
            project_repository: Project repository to get project key for issue key generation
            user_repository: User repository to verify assignee exists
            activity_repository: Issue activity repository for logging
            session: Database session (for consistency, not directly used here)
        """
        self._issue_repository = issue_repository
        self._project_repository = project_repository
        self._user_repository = user_repository
        self._activity_repository = activity_repository
        self._session = session

    async def execute(
        self, issue_id: str, request: UpdateIssueRequest, user_id: UUID | None = None
    ) -> IssueResponse:
        """Execute update issue.

        Args:
            issue_id: Issue ID
            request: Issue update request

        Returns:
            Updated issue response DTO

        Raises:
            EntityNotFoundException: If issue not found
            ValidationException: If issue data is invalid
        """
        logger.info("Updating issue", issue_id=issue_id)

        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)

        if issue is None:
            logger.warning("Issue not found for update", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Verify assignee exists if provided
        if request.assignee_id:
            assignee = await self._user_repository.get_by_id(request.assignee_id)
            if assignee is None:
                logger.warning("Assignee user not found", assignee_id=str(request.assignee_id))
                raise EntityNotFoundException("User", str(request.assignee_id))

        # Store old values for activity logging
        old_title = issue.title
        old_description = issue.description
        old_status = issue.status
        old_priority = issue.priority
        old_assignee_id = issue.assignee_id
        old_due_date = issue.due_date
        old_story_points = issue.story_points

        # Apply updates from DTO
        if request.title is not None:
            try:
                issue.update_title(request.title)
            except ValueError as e:
                raise ValidationException(str(e), field="title") from e

        if request.description is not None:
            issue.update_description(request.description)

        if request.status is not None:
            try:
                issue.update_status(request.status)
            except ValueError as e:
                raise ValidationException(str(e), field="status") from e

        if request.priority is not None:
            try:
                issue.update_priority(request.priority)
            except ValueError as e:
                raise ValidationException(str(e), field="priority") from e

        if request.assignee_id is not None:
            issue.update_assignee(request.assignee_id)

        if request.due_date is not None:
            issue.update_due_date(request.due_date)

        if request.story_points is not None:
            try:
                issue.update_story_points(request.story_points)
            except ValueError as e:
                raise ValidationException(str(e), field="story_points") from e

        # Save to database
        updated_issue = await self._issue_repository.update(issue)

        # Create activity logs for changed fields

        if request.title is not None and old_title != updated_issue.title:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="updated",
                field_name="title",
                old_value=old_title,
                new_value=updated_issue.title,
            )

        if request.description is not None and old_description != updated_issue.description:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="updated",
                field_name="description",
                old_value=old_description or "",
                new_value=updated_issue.description or "",
            )

        if request.status is not None and old_status != updated_issue.status:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="status_changed",
                field_name="status",
                old_value=old_status,
                new_value=updated_issue.status,
            )

        if request.priority is not None and old_priority != updated_issue.priority:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="updated",
                field_name="priority",
                old_value=old_priority,
                new_value=updated_issue.priority,
            )

        if request.assignee_id is not None and old_assignee_id != updated_issue.assignee_id:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="assigned",
                field_name="assignee_id",
                old_value=str(old_assignee_id) if old_assignee_id else None,
                new_value=str(updated_issue.assignee_id) if updated_issue.assignee_id else None,
            )

        if request.due_date is not None and old_due_date != updated_issue.due_date:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="updated",
                field_name="due_date",
                old_value=str(old_due_date) if old_due_date else None,
                new_value=str(updated_issue.due_date) if updated_issue.due_date else None,
            )

        if request.story_points is not None and old_story_points != updated_issue.story_points:
            await self._activity_repository.create(
                issue_id=updated_issue.id,
                user_id=user_id,
                action="updated",
                field_name="story_points",
                old_value=str(old_story_points) if old_story_points else None,
                new_value=str(updated_issue.story_points) if updated_issue.story_points else None,
            )

        # Get project to generate issue key
        project = await self._project_repository.get_by_id(updated_issue.project_id)
        if project is None:
            logger.warning(
                "Project not found for issue", project_id=str(updated_issue.project_id)
            )
            raise EntityNotFoundException("Project", str(updated_issue.project_id))

        # Generate issue key (PROJ-123 format)
        issue_key = updated_issue.generate_key(project.key)

        logger.info("Issue updated", issue_id=issue_id)

        # Convert to response DTO with key
        issue_dict = {
            "id": updated_issue.id,
            "project_id": updated_issue.project_id,
            "issue_number": updated_issue.issue_number,
            "key": issue_key,
            "title": updated_issue.title,
            "description": updated_issue.description,
            "type": updated_issue.type,
            "status": updated_issue.status,
            "priority": updated_issue.priority,
            "reporter_id": updated_issue.reporter_id,
            "assignee_id": updated_issue.assignee_id,
            "due_date": updated_issue.due_date,
            "story_points": updated_issue.story_points,
            "created_at": updated_issue.created_at,
            "updated_at": updated_issue.updated_at,
        }
        return IssueResponse.model_validate(issue_dict)

