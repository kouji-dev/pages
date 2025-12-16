"""Add issue to sprint use case."""

from uuid import UUID

import structlog

from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import IssueRepository, SprintRepository

logger = structlog.get_logger()


class AddIssueToSprintUseCase:
    """Use case for adding an issue to a sprint."""

    def __init__(
        self,
        sprint_repository: SprintRepository,
        issue_repository: IssueRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
            issue_repository: Issue repository to verify issue exists and belongs to project
        """
        self._sprint_repository = sprint_repository
        self._issue_repository = issue_repository

    async def execute(
        self,
        sprint_id: UUID,
        issue_id: UUID,
        order: int = 0,
    ) -> None:
        """Execute adding issue to sprint.

        Args:
            sprint_id: Sprint UUID
            issue_id: Issue UUID
            order: Order within the sprint (default: 0)

        Raises:
            EntityNotFoundException: If sprint or issue not found
            ConflictException: If issue belongs to different project or is already in another active sprint
        """
        logger.info(
            "Adding issue to sprint",
            sprint_id=str(sprint_id),
            issue_id=str(issue_id),
            order=order,
        )

        # Verify sprint exists
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Verify issue exists
        issue = await self._issue_repository.get_by_id(issue_id)
        if issue is None:
            logger.warning("Issue not found", issue_id=str(issue_id))
            raise EntityNotFoundException("Issue", str(issue_id))

        # Validate issue belongs to same project
        if issue.project_id != sprint.project_id:
            logger.warning(
                "Issue belongs to different project",
                issue_id=str(issue_id),
                issue_project_id=str(issue.project_id),
                sprint_project_id=str(sprint.project_id),
            )
            raise ConflictException(
                f"Issue {issue_id} belongs to a different project than sprint {sprint_id}"
            )

        # Check if issue is already in another active sprint
        existing_sprint = await self._sprint_repository.get_issue_sprint(issue_id)
        if existing_sprint is not None and existing_sprint.id != sprint_id:
            if existing_sprint.is_active():
                logger.warning(
                    "Issue already in active sprint",
                    issue_id=str(issue_id),
                    existing_sprint_id=str(existing_sprint.id),
                )
                raise ConflictException(
                    f"Issue {issue_id} is already in active sprint {existing_sprint.id}"
                )

        # Add issue to sprint
        await self._sprint_repository.add_issue_to_sprint(sprint_id, issue_id, order)

        logger.info(
            "Issue added to sprint successfully",
            sprint_id=str(sprint_id),
            issue_id=str(issue_id),
        )
