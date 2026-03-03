"""Create group board use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardResponse, CreateGroupBoardRequest
from src.domain.entities import Board
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import BoardRepository, OrganizationRepository, ProjectRepository

logger = structlog.get_logger()


class CreateGroupBoardUseCase:
    """Use case for creating an organization-level group board spanning multiple projects."""

    def __init__(
        self,
        board_repository: BoardRepository,
        organization_repository: OrganizationRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._organization_repository = organization_repository
        self._project_repository = project_repository

    async def execute(
        self,
        organization_id: UUID,
        request: CreateGroupBoardRequest,
        created_by: UUID | None = None,
    ) -> BoardResponse:
        """Create a new group board attached to an organization and multiple projects."""
        logger.info(
            "Creating group board",
            organization_id=str(organization_id),
            name=request.name,
            project_ids=[str(pid) for pid in request.project_ids],
        )

        org = await self._organization_repository.get_by_id(organization_id)
        if org is None:
            raise EntityNotFoundException("Organization", str(organization_id))

        if not request.project_ids:
            raise ValidationException("Group board must include at least one project")

        # Validate that all projects exist and belong to the organization
        validated_project_ids: list[UUID] = []
        for project_id in request.project_ids:
            project = await self._project_repository.get_by_id(project_id)
            if project is None:
                raise EntityNotFoundException("Project", str(project_id))
            if project.organization_id != organization_id:
                raise ValidationException(
                    "All projects of a group board must belong to the same organization"
                )
            validated_project_ids.append(project.id)

        primary_project_id = validated_project_ids[0]

        board = Board.create_group(
            organization_id=organization_id,
            primary_project_id=primary_project_id,
            name=request.name,
            description=request.description,
            scope_config=request.scope_config,
            is_default=request.is_default,
            position=request.position,
            created_by=created_by,
        )
        created = await self._board_repository.create(board)
        await self._board_repository.set_projects_for_group_board(
            created.id,
            validated_project_ids,
        )

        return BoardResponse(
            id=created.id,
            project_id=created.project_id,
            organization_id=created.organization_id,
            board_type=created.board_type,
            swimlane_type=created.swimlane_type,
            name=created.name,
            description=created.description,
            scope_config=created.scope_config,
            is_default=created.is_default,
            position=created.position,
            created_by=created.created_by,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
