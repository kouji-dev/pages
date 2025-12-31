"""Create sprint use case."""

from uuid import UUID

import structlog

from src.application.dtos.sprint import CreateSprintRequest, SprintResponse
from src.domain.entities import Sprint
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import ProjectRepository, SprintRepository

logger = structlog.get_logger()


class CreateSprintUseCase:
    """Use case for creating a sprint."""

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
        request: CreateSprintRequest,
    ) -> SprintResponse:
        """Execute sprint creation.

        Args:
            project_id: ID of the project to create the sprint in
            request: Sprint creation request

        Returns:
            Created sprint response DTO

        Raises:
            EntityNotFoundException: If project not found
            ConflictException: If sprint dates overlap with existing sprints
            ValueError: If dates are invalid
        """
        logger.info(
            "Creating sprint",
            name=request.name,
            project_id=str(project_id),
        )

        # Verify project exists
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            logger.warning(
                "Project not found for sprint creation",
                project_id=str(project_id),
            )
            raise EntityNotFoundException("Project", str(project_id))

        # Validate dates
        if request.start_date and request.end_date:
            if request.start_date >= request.end_date:
                raise ValueError("Sprint start date must be before end date")

        # Check for overlapping sprints if dates are provided
        if request.start_date and request.end_date:
            overlapping = await self._sprint_repository.find_overlapping_sprints(
                project_id=project_id,
                start_date=request.start_date,
                end_date=request.end_date,
            )
            if overlapping:
                logger.warning(
                    "Overlapping sprint found",
                    project_id=str(project_id),
                    start_date=str(request.start_date),
                    end_date=str(request.end_date),
                )
                raise ConflictException(
                    f"Sprint dates overlap with existing sprint: {overlapping[0].name}"
                )

        # Create sprint entity
        sprint = Sprint.create(
            project_id=project_id,
            name=request.name,
            goal=request.goal,
            start_date=request.start_date,
            end_date=request.end_date,
            status=request.status,
        )

        # Persist sprint
        created_sprint = await self._sprint_repository.create(sprint)

        logger.info(
            "Sprint created successfully",
            sprint_id=str(created_sprint.id),
            project_id=str(project_id),
        )

        # Get issue counts (will be 0 for new sprint)
        total_issues, completed_issues = await self._sprint_repository.get_sprint_issue_counts(
            created_sprint.id
        )

        sprint_dict = {
            "id": created_sprint.id,
            "project_id": created_sprint.project_id,
            "name": created_sprint.name,
            "goal": created_sprint.goal,
            "start_date": created_sprint.start_date,
            "end_date": created_sprint.end_date,
            "status": created_sprint.status,
            "total_issues": total_issues,
            "completed_issues": completed_issues,
            "created_at": created_sprint.created_at,
            "updated_at": created_sprint.updated_at,
        }

        return SprintResponse.model_validate(sprint_dict)
