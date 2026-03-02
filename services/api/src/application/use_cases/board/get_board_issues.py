"""Get board issues (grouped by list) use case."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import structlog

from src.application.dtos.board import (
    BoardIssueItemResponse,
    BoardIssuesResponse,
    BoardListWithIssuesResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    BoardRepository,
    CommentRepository,
    IssueRepository,
    LabelRepository,
    ProjectRepository,
)

if TYPE_CHECKING:
    from src.domain.entities import Issue
    from src.domain.entities.board import BoardList

logger = structlog.get_logger()

# Max issues per column to avoid unbounded load
BOARD_ISSUES_LIMIT_PER_LIST = 500


class GetBoardIssuesUseCase:
    """Use case for GET /boards/:id/issues — issues grouped by list with scope applied."""

    def __init__(
        self,
        board_repository: BoardRepository,
        issue_repository: IssueRepository,
        label_repository: LabelRepository,
        comment_repository: CommentRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._board_repository = board_repository
        self._issue_repository = issue_repository
        self._label_repository = label_repository
        self._comment_repository = comment_repository
        self._project_repository = project_repository

    async def execute(self, board_id: UUID) -> BoardIssuesResponse:
        """Load board, apply scope, for each list load issues and build list-with-issues DTOs."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))

        project = await self._project_repository.get_by_id(board.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(board.project_id))

        project_key = project.key
        scope_config = board.scope_config or {}
        scope_label_ids: list[UUID] = _extract_label_ids(scope_config.get("label_ids"))

        lists = await self._board_repository.get_lists_for_board(board_id)
        list_dtos: list[BoardListWithIssuesResponse] = []

        for lst in lists:
            issues = await self._load_issues_for_list(board.project_id, lst)
            items: list[BoardIssueItemResponse] = []
            for issue in issues:
                label_entities = await self._label_repository.get_labels_for_issue(issue.id)
                label_ids = [lab.id for lab in label_entities]
                if scope_label_ids and not any(lid in scope_label_ids for lid in label_ids):
                    continue
                comment_count = await self._comment_repository.count_by_issue_id(issue.id)
                subtask_count = await self._issue_repository.count(
                    board.project_id,
                    parent_issue_id=issue.id,
                )
                items.append(
                    BoardIssueItemResponse(
                        id=issue.id,
                        issue_number=issue.issue_number,
                        key=issue.generate_key(project_key),
                        title=issue.title,
                        type=issue.type,
                        status=issue.status,
                        priority=issue.priority,
                        assignee_id=issue.assignee_id,
                        story_points=issue.story_points,
                        label_ids=label_ids,
                        comment_count=comment_count,
                        subtask_count=subtask_count,
                    )
                )
            list_dtos.append(
                BoardListWithIssuesResponse(
                    id=lst.id,
                    board_id=lst.board_id,
                    list_type=lst.list_type,
                    list_config=lst.list_config,
                    position=lst.position,
                    issues=items,
                )
            )

        return BoardIssuesResponse(lists=list_dtos)

    async def _load_issues_for_list(
        self,
        project_id: UUID,
        lst: BoardList,
    ) -> list[Issue]:
        """Load issues for one board list based on list_type and list_config."""
        list_config = lst.list_config or {}
        label_ids: list[UUID] | None = None
        assignee_id: UUID | None = None
        sprint_id: UUID | None = None

        if lst.list_type == "label":
            lid = list_config.get("label_id")
            if lid is not None:
                label_ids = [lid if isinstance(lid, UUID) else UUID(str(lid))]
        elif lst.list_type == "assignee":
            uid = list_config.get("user_id")
            if uid is not None:
                assignee_id = uid if isinstance(uid, UUID) else UUID(str(uid))
        elif lst.list_type == "milestone":
            sid = list_config.get("sprint_id")
            if sid is not None:
                sprint_id = sid if isinstance(sid, UUID) else UUID(str(sid))

        return await self._issue_repository.get_all(
            project_id,
            skip=0,
            limit=BOARD_ISSUES_LIMIT_PER_LIST,
            assignee_id=assignee_id,
            label_ids=label_ids,
            sprint_id=sprint_id,
        )


def _extract_label_ids(value: object) -> list[UUID]:
    """Extract list of UUIDs from scope_config label_ids (may be list of str or UUID)."""
    if not value or not isinstance(value, list):
        return []
    out: list[UUID] = []
    for v in value:
        if isinstance(v, UUID):
            out.append(v)
        elif isinstance(v, str):
            try:
                out.append(UUID(v))
            except (ValueError, TypeError):
                pass
    return out
