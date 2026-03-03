"""Get board issues (grouped by list) use case."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import structlog

from src.application.dtos.board import (
    BoardIssueItemResponse,
    BoardIssuesResponse,
    BoardListWithIssuesResponse,
    BoardSwimlaneResponse,
    SwimlaneAssigneeSummary,
)
from src.domain.entities.board import BoardList
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    BoardRepository,
    CommentRepository,
    IssueRepository,
    LabelRepository,
    ProjectRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from src.domain.entities import Issue

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
        user_repository: UserRepository | None = None,
    ) -> None:
        self._board_repository = board_repository
        self._issue_repository = issue_repository
        self._label_repository = label_repository
        self._comment_repository = comment_repository
        self._project_repository = project_repository
        self._user_repository = user_repository

    async def execute(self, board_id: UUID) -> BoardIssuesResponse:
        """Load board, apply scope, for each list load issues and build list-with-issues DTOs."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))

        # Determine projects participating in this board
        if board.board_type == "group":
            project_ids = await self._board_repository.get_projects_for_board(board_id)
            if not project_ids:
                # Fallback to primary project to avoid hard failure
                project_ids = [board.project_id]
        else:
            project_ids = [board.project_id]

        from src.domain.entities import Project

        projects_by_id: dict[UUID, Project] = {}
        for pid in project_ids:
            project = await self._project_repository.get_by_id(pid)
            if project is None:
                raise EntityNotFoundException("Project", str(pid))
            projects_by_id[pid] = project
        scope_config = board.scope_config or {}
        scope_label_ids: list[UUID] = _extract_label_ids(scope_config.get("label_ids"))
        scope_exclude_label_ids: list[UUID] = _extract_label_ids(
            scope_config.get("exclude_label_ids")
        )
        scope_assignee_id = _extract_uuid(scope_config.get("assignee_id"))
        fixed_user_id = _extract_uuid(scope_config.get("fixed_user_id"))
        if fixed_user_id and not scope_assignee_id:
            scope_assignee_id = fixed_user_id
        scope_sprint_id = _extract_uuid(scope_config.get("milestone_id"))
        scope_types = _extract_scope_str_list(
            scope_config.get("types"), {"task", "bug", "story", "epic"}
        )
        scope_priorities = _extract_scope_str_list(
            scope_config.get("priorities"), {"low", "medium", "high", "critical"}
        )
        scope_reporter_id = _extract_uuid(scope_config.get("reporter_id"))
        raw_search = scope_config.get("search_text")
        scope_search_text = raw_search.strip().lower() if isinstance(raw_search, str) else ""
        scope_story_min = scope_config.get("story_points_min")
        scope_story_max = scope_config.get("story_points_max")

        lists = await self._board_repository.get_lists_for_board(board_id)
        list_dtos: list[BoardListWithIssuesResponse] = []
        # For swimlanes: (swimlane_key, list, item) then group by swimlane_key
        swimlane_cells: list[tuple[UUID | None, BoardList, BoardIssueItemResponse]] = []

        for lst in lists:
            issues = await self._load_issues_for_list(
                project_ids,
                lst,
                scope_assignee_id=scope_assignee_id,
                scope_sprint_id=scope_sprint_id,
                scope_reporter_id=scope_reporter_id,
            )
            items: list[BoardIssueItemResponse] = []
            for issue in issues:
                label_entities = await self._label_repository.get_labels_for_issue(issue.id)
                label_ids = [lab.id for lab in label_entities]
                if scope_label_ids and not any(lid in scope_label_ids for lid in label_ids):
                    continue
                if scope_exclude_label_ids and any(
                    lid in scope_exclude_label_ids for lid in label_ids
                ):
                    continue
                if (
                    scope_assignee_id
                    and issue.assignee_id
                    and issue.assignee_id != scope_assignee_id
                ):
                    continue
                if scope_types and issue.type not in scope_types:
                    continue
                if scope_priorities and issue.priority not in scope_priorities:
                    continue
                if (
                    scope_reporter_id
                    and issue.reporter_id
                    and issue.reporter_id != scope_reporter_id
                ):
                    continue
                if scope_search_text:
                    haystack = f"{(issue.title or '').lower()} {(getattr(issue, 'description', '') or '').lower()}"
                    if scope_search_text not in haystack:
                        continue
                if scope_story_min is not None:
                    if issue.story_points is None or issue.story_points < scope_story_min:
                        continue
                if scope_story_max is not None:
                    if issue.story_points is None or issue.story_points > scope_story_max:
                        continue
                project = projects_by_id.get(issue.project_id)
                if project is None:
                    continue
                project_key = project.key
                comment_count = await self._comment_repository.count_by_issue_id(issue.id)
                subtask_count = await self._issue_repository.count(
                    issue.project_id,
                    parent_issue_id=issue.id,
                )
                item = BoardIssueItemResponse(
                    id=issue.id,
                    issue_number=issue.issue_number,
                    key=issue.generate_key(project_key),
                    project_id=issue.project_id,
                    project_key=project_key,
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
                items.append(item)
                if board.swimlane_type == "epic":
                    swimlane_cells.append((issue.parent_issue_id, lst, item))
                elif board.swimlane_type == "assignee":
                    swimlane_cells.append((issue.assignee_id, lst, item))
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

        if board.swimlane_type == "none":
            return BoardIssuesResponse(
                lists=list_dtos,
                swimlane_type="none",
                swimlanes=[],
            )

        # Build swimlanes from swimlane_cells
        swimlanes_dto = await self._build_swimlanes(
            board.swimlane_type,
            swimlane_cells,
            lists,
        )
        return BoardIssuesResponse(
            lists=[],
            swimlane_type=board.swimlane_type,
            swimlanes=swimlanes_dto,
        )

    async def _build_swimlanes(
        self,
        swimlane_type: str,
        swimlane_cells: list[tuple[UUID | None, BoardList, BoardIssueItemResponse]],
        lists: list[BoardList],
    ) -> list[BoardSwimlaneResponse]:
        """Group cells by swimlane key and build swimlane DTOs with metadata."""
        from collections import defaultdict

        # Group by swimlane_key -> list_id -> [items]
        by_key: dict[UUID | None, dict[UUID, list[BoardIssueItemResponse]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for swimlane_key, lst, item in swimlane_cells:
            by_key[swimlane_key][lst.id].append(item)

        # Order keys: None first (no epic / unassigned), then stable order
        keys_ordered: list[UUID | None] = []
        seen: set[UUID | None] = set()
        for k in by_key:
            if k not in seen:
                keys_ordered.append(k)
                seen.add(k)
        # Put None at the beginning if present
        if None in keys_ordered:
            keys_ordered.remove(None)
            keys_ordered.insert(0, None)

        result: list[BoardSwimlaneResponse] = []
        for swimlane_id in keys_ordered:
            list_id_to_items = by_key[swimlane_id]
            list_dtos_for_swimlane: list[BoardListWithIssuesResponse] = []
            for lst in lists:
                items_in_cell = list_id_to_items.get(lst.id, [])
                list_dtos_for_swimlane.append(
                    BoardListWithIssuesResponse(
                        id=lst.id,
                        board_id=lst.board_id,
                        list_type=lst.list_type,
                        list_config=lst.list_config,
                        position=lst.position,
                        issues=items_in_cell,
                    )
                )
            if swimlane_type == "epic":
                if swimlane_id is None:
                    title = "No epic"
                else:
                    epic_issue = await self._issue_repository.get_by_id(swimlane_id)
                    title = epic_issue.title if epic_issue else f"Epic {swimlane_id}"
                assignee_summary = None
            else:
                if swimlane_id is None:
                    title = "Unassigned"
                    assignee_summary = None
                else:
                    user = (
                        await self._user_repository.get_by_id(swimlane_id)
                        if self._user_repository
                        else None
                    )
                    title = user.name if user else str(swimlane_id)
                    assignee_summary = (
                        SwimlaneAssigneeSummary(
                            id=swimlane_id,
                            name=user.name,
                            avatar_url=user.avatar_url,
                        )
                        if user
                        else SwimlaneAssigneeSummary(id=swimlane_id, name=title)
                    )
            result.append(
                BoardSwimlaneResponse(
                    swimlane_id=swimlane_id,
                    swimlane_title=title,
                    assignee=assignee_summary,
                    lists=list_dtos_for_swimlane,
                )
            )
        return result

    async def _load_issues_for_list(
        self,
        project_ids: list[UUID],
        lst: BoardList,
        scope_assignee_id: UUID | None,
        scope_sprint_id: UUID | None,
        scope_reporter_id: UUID | None,
    ) -> list[Issue]:
        """Load issues for one board list across one or many projects."""
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

        # Apply global assignee/sprint scope on top of list-based filters (intersection).
        if scope_assignee_id:
            if assignee_id and assignee_id != scope_assignee_id:
                return []
            assignee_id = scope_assignee_id
        if scope_sprint_id:
            if sprint_id and sprint_id != scope_sprint_id:
                return []
            sprint_id = scope_sprint_id

        issues: list[Issue] = []
        for project_id in project_ids:
            batch = await self._issue_repository.get_all(
                project_id,
                skip=0,
                limit=BOARD_ISSUES_LIMIT_PER_LIST,
                assignee_id=assignee_id,
                reporter_id=scope_reporter_id,
                label_ids=label_ids,
                sprint_id=sprint_id,
            )
            issues.extend(batch)
        return issues


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


def _extract_uuid(value: object | None) -> UUID | None:
    """Extract UUID from a value that may be UUID or str; invalid values yield None."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except (ValueError, TypeError):
            return None
    return None


def _extract_scope_str_list(value: object | None, allowed: set[str]) -> list[str]:
    """Extract a list of strings for scope filters, keeping only allowed values."""
    if not value or not isinstance(value, list):
        return []
    out: list[str] = []
    for v in value:
        if isinstance(v, str) and v in allowed and v not in out:
            out.append(v)
    return out
