"""Get sprint use case."""

from uuid import UUID

import structlog

from src.application.dtos.sprint import SprintWithIssuesResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import SprintRepository

logger = structlog.get_logger()


class GetSprintUseCase:
    """Use case for getting a sprint by ID."""

    def __init__(self, sprint_repository: SprintRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
        """
        self._sprint_repository = sprint_repository

    async def execute(self, sprint_id: UUID) -> SprintWithIssuesResponse:
        """Execute sprint retrieval.

        Args:
            sprint_id: Sprint UUID

        Returns:
            Sprint response DTO with issues

        Raises:
            EntityNotFoundException: If sprint not found
        """
        logger.info("Getting sprint", sprint_id=str(sprint_id))

        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Get sprint issues
        sprint_issues = await self._sprint_repository.get_sprint_issues(sprint_id)
        issue_ids = [issue_id for issue_id, _ in sprint_issues]

        sprint_dict = {
            "id": sprint.id,
            "project_id": sprint.project_id,
            "name": sprint.name,
            "goal": sprint.goal,
            "start_date": sprint.start_date,
            "end_date": sprint.end_date,
            "status": sprint.status,
            "issues": issue_ids,
            "created_at": sprint.created_at,
            "updated_at": sprint.updated_at,
        }

        return SprintWithIssuesResponse.model_validate(sprint_dict)
