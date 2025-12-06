"""Get issue use case."""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.issue import IssueResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository, ProjectRepository

logger = structlog.get_logger()


class GetIssueUseCase:
    """Use case for retrieving an issue."""

    def __init__(
        self,
        issue_repository: IssueRepository,
        project_repository: ProjectRepository,
        session: AsyncSession,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            issue_repository: Issue repository for data access
            project_repository: Project repository to get project key for issue key generation
            session: Database session (for consistency, not directly used here)
        """
        self._issue_repository = issue_repository
        self._project_repository = project_repository
        self._session = session

    async def execute(self, issue_id: str) -> IssueResponse:
        """Execute get issue.

        Args:
            issue_id: Issue ID

        Returns:
            Issue response DTO with key

        Raises:
            EntityNotFoundException: If issue not found
        """
        logger.info("Getting issue", issue_id=issue_id)

        issue_uuid = UUID(issue_id)
        issue = await self._issue_repository.get_by_id(issue_uuid)

        if issue is None:
            logger.warning("Issue not found", issue_id=issue_id)
            raise EntityNotFoundException("Issue", issue_id)

        # Get project to generate issue key
        project = await self._project_repository.get_by_id(issue.project_id)
        if project is None:
            logger.warning("Project not found for issue", project_id=str(issue.project_id))
            raise EntityNotFoundException("Project", str(issue.project_id))

        # Generate issue key (PROJ-123 format)
        issue_key = issue.generate_key(project.key)

        # Convert to response DTO with key
        issue_dict = {
            "id": issue.id,
            "project_id": issue.project_id,
            "issue_number": issue.issue_number,
            "key": issue_key,
            "title": issue.title,
            "description": issue.description,
            "type": issue.type,
            "status": issue.status,
            "priority": issue.priority,
            "reporter_id": issue.reporter_id,
            "assignee_id": issue.assignee_id,
            "due_date": issue.due_date,
            "story_points": issue.story_points,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
        }
        return IssueResponse.model_validate(issue_dict)
