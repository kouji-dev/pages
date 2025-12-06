"""Create issue use case."""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue import CreateIssueRequest, IssueResponse
from src.domain.entities import Issue
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    IssueActivityRepository,
    IssueRepository,
    ProjectRepository,
    UserRepository,
)

logger = structlog.get_logger()


class CreateIssueUseCase:
    """Use case for creating an issue."""

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
            issue_repository: Issue repository
            project_repository: Project repository to verify project exists and get project key
            user_repository: User repository to verify reporter exists
            activity_repository: Issue activity repository for logging
            session: Database session (for consistency, not directly used here)
        """
        self._issue_repository = issue_repository
        self._project_repository = project_repository
        self._user_repository = user_repository
        self._activity_repository = activity_repository
        self._session = session

    async def execute(self, request: CreateIssueRequest, reporter_user_id: str) -> IssueResponse:
        """Execute issue creation.

        Args:
            request: Issue creation request
            reporter_user_id: ID of the user reporting the issue

        Returns:
            Created issue response DTO

        Raises:
            EntityNotFoundException: If project or reporter user not found
        """
        logger.info(
            "Creating issue",
            project_id=str(request.project_id),
            title=request.title,
            type=request.type,
            reporter_user_id=reporter_user_id,
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(request.project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(request.project_id))
            raise EntityNotFoundException("Project", str(request.project_id))

        # Verify reporter exists
        reporter_uuid = UUID(reporter_user_id)
        reporter = await self._user_repository.get_by_id(reporter_uuid)
        if reporter is None:
            logger.warning("Reporter user not found", reporter_user_id=reporter_user_id)
            raise EntityNotFoundException("User", reporter_user_id)

        # Verify assignee exists if provided
        if request.assignee_id:
            assignee = await self._user_repository.get_by_id(request.assignee_id)
            if assignee is None:
                logger.warning("Assignee user not found", assignee_id=str(request.assignee_id))
                raise EntityNotFoundException("User", str(request.assignee_id))

        # Get next issue number (atomic operation)
        issue_number = await self._issue_repository.get_next_issue_number(request.project_id)

        # Create issue entity
        issue = Issue.create(
            project_id=request.project_id,
            issue_number=issue_number,
            title=request.title,
            description=request.description,
            type=request.type,
            status=request.status,
            priority=request.priority,
            reporter_id=reporter_uuid,
            assignee_id=request.assignee_id,
            due_date=request.due_date,
            story_points=request.story_points,
        )

        # Persist issue
        created_issue = await self._issue_repository.create(issue)

        # Create activity log for issue creation
        await self._activity_repository.create(
            issue_id=created_issue.id,
            user_id=reporter_uuid,
            action="created",
        )

        # Generate issue key (PROJ-123 format)
        issue_key = created_issue.generate_key(project.key)

        logger.info(
            "Issue created successfully",
            issue_id=str(created_issue.id),
            issue_key=issue_key,
            issue_number=issue_number,
        )

        # Convert to response DTO with key
        issue_dict = {
            "id": created_issue.id,
            "project_id": created_issue.project_id,
            "issue_number": created_issue.issue_number,
            "key": issue_key,
            "title": created_issue.title,
            "description": created_issue.description,
            "type": created_issue.type,
            "status": created_issue.status,
            "priority": created_issue.priority,
            "reporter_id": created_issue.reporter_id,
            "assignee_id": created_issue.assignee_id,
            "due_date": created_issue.due_date,
            "story_points": created_issue.story_points,
            "created_at": created_issue.created_at,
            "updated_at": created_issue.updated_at,
        }
        return IssueResponse.model_validate(issue_dict)
