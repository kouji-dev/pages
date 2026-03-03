"""Update board scope configuration use case."""

from uuid import UUID

import structlog

from src.application.dtos.board import BoardResponse, UpdateBoardScopeRequest
from src.domain.entities.board import BoardList
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import BoardRepository, ProjectRepository

logger = structlog.get_logger()


class UpdateBoardScopeUseCase:
    """Use case for updating board scope configuration (scope_config JSON)."""

    def __init__(
        self,
        board_repository: BoardRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._project_repository = project_repository

    async def execute(self, board_id: UUID, request: UpdateBoardScopeRequest) -> BoardResponse:
        """Validate and update scope_config for a board."""
        logger.info("Updating board scope", board_id=str(board_id))
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))

        project = await self._project_repository.get_by_id(board.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(board.project_id))

        lists = await self._board_repository.get_lists_for_board(board_id)
        self._validate_scope(request, lists)

        scope_config = request.model_dump(exclude_none=True)
        # Ensure JSON-serializable values for IDs (store as strings).
        for key in ("label_ids", "exclude_label_ids"):
            if key in scope_config:
                scope_config[key] = [str(v) for v in scope_config[key]]
        for key in ("assignee_id", "milestone_id", "fixed_user_id", "reporter_id"):
            if scope_config.get(key) is not None:
                scope_config[key] = str(scope_config[key])
        board.update_scope_config(scope_config)
        updated = await self._board_repository.update(board)
        return BoardResponse(
            id=updated.id,
            project_id=updated.project_id,
            organization_id=updated.organization_id,
            board_type=updated.board_type,
            swimlane_type=updated.swimlane_type,
            name=updated.name,
            description=updated.description,
            scope_config=updated.scope_config,
            is_default=updated.is_default,
            position=updated.position,
            created_by=updated.created_by,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    def _validate_scope(
        self,
        request: UpdateBoardScopeRequest,
        lists: list[BoardList],
    ) -> None:
        """Validate that scope config is self-consistent and does not conflict with lists."""
        # Labels include/exclude must not overlap
        if request.label_ids and request.exclude_label_ids:
            include_set = set(request.label_ids)
            exclude_set = set(request.exclude_label_ids)
            if include_set & exclude_set:
                raise ValidationException(
                    "Scope label_ids and exclude_label_ids cannot overlap",
                )

        # Fixed user is an alias of assignee filter; if both are set, they must match
        if (
            request.assignee_id
            and request.fixed_user_id
            and (request.assignee_id != request.fixed_user_id)
        ):
            raise ValidationException(
                "assignee_id and fixed_user_id must be equal when both are set",
            )

        effective_user = request.fixed_user_id or request.assignee_id
        if effective_user:
            for lst in lists:
                if lst.list_type == "assignee":
                    list_user = (lst.list_config or {}).get("user_id")
                    if list_user is not None and UUID(str(list_user)) != effective_user:
                        raise ValidationException(
                            "Scope fixed_user_id/assignee_id conflicts with assignee board lists",
                        )

        # Validate story points range
        if (
            request.story_points_min is not None
            and request.story_points_max is not None
            and request.story_points_min > request.story_points_max
        ):
            raise ValidationException(
                "story_points_min cannot be greater than story_points_max",
            )
