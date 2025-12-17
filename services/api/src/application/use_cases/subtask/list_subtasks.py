"""List subtasks use case."""

from uuid import UUID

import structlog

from src.application.dtos.issue import IssueListItemResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import IssueRepository

logger = structlog.get_logger()


class ListSubtasksUseCase:
    """Use case for listing subtasks of an issue."""

    def __init__(self, issue_repository: IssueRepository) -> None:
        """Initialize use case with dependencies."""
        self._issue_repository = issue_repository

    async def execute(self, issue_id: UUID) -> list[IssueListItemResponse]:
        """Execute list subtasks."""
        logger.info("Listing subtasks", issue_id=str(issue_id))

        # Verify parent issue exists
        parent_issue = await self._issue_repository.get_by_id(issue_id)
        if parent_issue is None:
            logger.warning("Parent issue not found", issue_id=str(issue_id))
            raise EntityNotFoundException("Issue", str(issue_id))

        # Get all issues with this issue as parent
        # Use get_all with a large limit to get all issues in the project
        issues = await self._issue_repository.get_all(
            project_id=parent_issue.project_id,
            skip=0,
            limit=10000,  # Large limit to get all issues
        )

        # Filter subtasks
        subtasks = [issue for issue in issues if issue.parent_issue_id == issue_id]

        # Convert to response DTOs
        subtask_items = [
            IssueListItemResponse.model_validate(
                {
                    "id": s.id,
                    "project_id": s.project_id,
                    "issue_number": s.issue_number,
                    "key": f"PROJ-{s.issue_number}",  # Will be replaced with actual project key
                    "title": s.title,
                    "type": s.type,
                    "status": s.status,
                    "priority": s.priority,
                    "reporter_id": s.reporter_id,
                    "assignee_id": s.assignee_id,
                    "due_date": s.due_date,
                    "story_points": s.story_points,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
            )
            for s in subtasks
        ]

        return subtask_items
