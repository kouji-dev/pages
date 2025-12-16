"""Update sprint use case."""

from uuid import UUID

import structlog

from src.application.dtos.sprint import SprintResponse, UpdateSprintRequest
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import SprintRepository

logger = structlog.get_logger()


class UpdateSprintUseCase:
    """Use case for updating a sprint."""

    def __init__(self, sprint_repository: SprintRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            sprint_repository: Sprint repository
        """
        self._sprint_repository = sprint_repository

    async def execute(
        self,
        sprint_id: UUID,
        request: UpdateSprintRequest,
    ) -> SprintResponse:
        """Execute sprint update.

        Args:
            sprint_id: Sprint UUID
            request: Sprint update request

        Returns:
            Updated sprint response DTO

        Raises:
            EntityNotFoundException: If sprint not found
            ConflictException: If sprint dates overlap with existing sprints
            ValueError: If dates are invalid
        """
        logger.info("Updating sprint", sprint_id=str(sprint_id))

        # Get existing sprint
        sprint = await self._sprint_repository.get_by_id(sprint_id)
        if sprint is None:
            logger.warning("Sprint not found", sprint_id=str(sprint_id))
            raise EntityNotFoundException("Sprint", str(sprint_id))

        # Update fields
        if request.name is not None:
            sprint.update_name(request.name)

        if request.goal is not None:
            sprint.update_goal(request.goal)

        # Handle date updates
        new_start_date = request.start_date if request.start_date is not None else sprint.start_date
        new_end_date = request.end_date if request.end_date is not None else sprint.end_date

        if new_start_date is not None and new_end_date is not None:
            if new_start_date >= new_end_date:
                raise ValueError("Sprint start date must be before end date")

            # Check for overlapping sprints (excluding current sprint)
            overlapping = await self._sprint_repository.find_overlapping_sprints(
                project_id=sprint.project_id,
                start_date=new_start_date,
                end_date=new_end_date,
                exclude_sprint_id=sprint_id,
            )
            if overlapping:
                logger.warning(
                    "Overlapping sprint found",
                    sprint_id=str(sprint_id),
                    start_date=str(new_start_date),
                    end_date=str(new_end_date),
                )
                raise ConflictException(
                    f"Sprint dates overlap with existing sprint: {overlapping[0].name}"
                )

            sprint.update_dates(new_start_date, new_end_date)
        elif request.start_date is not None or request.end_date is not None:
            # Partial date update
            sprint.update_dates(new_start_date, new_end_date)

        if request.status is not None:
            sprint.update_status(request.status)

        # Persist changes
        updated_sprint = await self._sprint_repository.update(sprint)

        logger.info("Sprint updated successfully", sprint_id=str(sprint_id))

        return SprintResponse.model_validate(updated_sprint)
