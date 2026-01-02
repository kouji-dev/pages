"""List sprints use case."""

from uuid import UUID

import structlog

from src.application.dtos.sprint import SprintListItemResponse, SprintListResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import ProjectRepository, SprintRepository
from src.domain.value_objects.sprint_status import SprintStatus

logger = structlog.get_logger()


class ListSprintsUseCase:
    """Use case for listing sprints in a project."""

    def __init__(
        self,
        sprint_repository: SprintRepository,
        project_repository: ProjectRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
            project_repository: Project repository to verify project exists
        """
        self._sprint_repository = sprint_repository
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: SprintStatus | None = None,
    ) -> SprintListResponse:
        """Execute sprint listing.

        Args:
            project_id: Project UUID
            page: Page number (1-indexed)
            limit: Number of items per page
            status: Optional status filter

        Returns:
            Paginated sprint list response DTO

        Raises:
            EntityNotFoundException: If project not found
        """
        logger.info(
            "Listing sprints",
            project_id=str(project_id),
            page=page,
            limit=limit,
            status=status.value if status else None,
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning("Project not found", project_id=str(project_id))
            raise EntityNotFoundException("Project", str(project_id))

        # Get sprints
        sprints = await self._sprint_repository.get_all(
            project_id=project_id,
            page=page,
            limit=limit,
            status=status,
        )

        # Get total count
        total = await self._sprint_repository.count(
            project_id=project_id,
            status=status,
        )

        # Calculate pages
        pages = (total + limit - 1) // limit if total > 0 else 0

        # Build sprint items with issue counts
        sprint_items = []
        for sprint in sprints:
            total_issues, completed_issues = await self._sprint_repository.get_sprint_issue_counts(
                sprint.id
            )
            sprint_dict = {
                "id": sprint.id,
                "project_id": sprint.project_id,
                "name": sprint.name,
                "goal": sprint.goal,
                "start_date": sprint.start_date,
                "end_date": sprint.end_date,
                "status": sprint.status,
                "total_issues": total_issues,
                "completed_issues": completed_issues,
                "created_at": sprint.created_at,
                "updated_at": sprint.updated_at,
            }
            sprint_items.append(SprintListItemResponse.model_validate(sprint_dict))

        return SprintListResponse(
            sprints=sprint_items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
