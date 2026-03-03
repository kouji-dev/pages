"""Move issue between board lists (drag & drop) with label/assignee/milestone swapping."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import structlog

from src.application.dtos.board import BoardIssueItemResponse
from src.domain.entities.board import BoardList
from src.domain.exceptions import ConflictException, EntityNotFoundException

if TYPE_CHECKING:
    from src.domain.entities import Issue
from src.domain.repositories import (
    BoardRepository,
    CommentRepository,
    IssueActivityRepository,
    IssueRepository,
    LabelRepository,
    ProjectRepository,
    SprintRepository,
)

logger = structlog.get_logger()

ACTION_BOARD_MOVE = "board_move"


class MoveBoardIssueUseCase:
    """Use case for moving an issue between board lists (drag & drop with label swapping)."""

    def __init__(
        self,
        board_repository: BoardRepository,
        issue_repository: IssueRepository,
        label_repository: LabelRepository,
        sprint_repository: SprintRepository,
        comment_repository: CommentRepository,
        project_repository: ProjectRepository,
        issue_activity_repository: IssueActivityRepository,
    ) -> None:
        self._board_repository = board_repository
        self._issue_repository = issue_repository
        self._label_repository = label_repository
        self._sprint_repository = sprint_repository
        self._comment_repository = comment_repository
        self._project_repository = project_repository
        self._issue_activity_repository = issue_activity_repository

    async def execute(
        self,
        board_id: UUID,
        issue_id: UUID,
        source_list_id: UUID,
        target_list_id: UUID,
        user_id: UUID | None = None,
    ) -> BoardIssueItemResponse:
        """Move issue from source list to target list; apply label/assignee/milestone swapping."""
        board = await self._board_repository.get_by_id(board_id)
        if board is None:
            raise EntityNotFoundException("Board", str(board_id))

        project = await self._project_repository.get_by_id(board.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(board.project_id))

        issue = await self._issue_repository.get_by_id(issue_id)
        if issue is None:
            raise EntityNotFoundException("Issue", str(issue_id))

        if board.board_type == "group":
            # For group boards, ensure the issue's project is part of the board projects
            project_ids = await self._board_repository.get_projects_for_board(board_id)
            if issue.project_id not in project_ids:
                raise EntityNotFoundException("Issue", str(issue_id))
        else:
            if issue.project_id != board.project_id:
                raise EntityNotFoundException("Issue", str(issue_id))

        scope_config = board.scope_config or {}
        scope_label_ids: list[UUID] = _extract_label_ids(scope_config.get("label_ids"))
        if scope_label_ids:
            issue_labels = await self._label_repository.get_labels_for_issue(issue_id)
            issue_label_ids = [lab.id for lab in issue_labels]
            if not any(lid in scope_label_ids for lid in issue_label_ids):
                raise EntityNotFoundException("Issue", str(issue_id))

        source_list = await self._board_repository.get_board_list_by_id(source_list_id)
        if source_list is None or source_list.board_id != board_id:
            raise EntityNotFoundException("BoardList", str(source_list_id))
        target_list = await self._board_repository.get_board_list_by_id(target_list_id)
        if target_list is None or target_list.board_id != board_id:
            raise EntityNotFoundException("BoardList", str(target_list_id))

        if source_list_id == target_list_id:
            return await self._build_issue_response(issue, project.key, issue.project_id)

        await self._apply_source_list_actions(issue, source_list)
        await self._apply_target_list_actions(issue, target_list, board.project_id)

        updated_issue = await self._issue_repository.get_by_id(issue_id)
        if updated_issue is None:
            raise EntityNotFoundException("Issue", str(issue_id))

        await self._issue_activity_repository.create(
            issue_id=issue_id,
            user_id=user_id,
            action=ACTION_BOARD_MOVE,
            field_name="board_list",
            old_value=str(source_list_id),
            new_value=str(target_list_id),
        )

        logger.info(
            "Board issue moved",
            board_id=str(board_id),
            issue_id=str(issue_id),
            source_list_id=str(source_list_id),
            target_list_id=str(target_list_id),
        )
        return await self._build_issue_response(updated_issue, project.key, board.project_id)

    async def _apply_source_list_actions(self, issue: Issue, source_list: BoardList) -> None:
        """Remove label / clear assignee / remove from sprint for source list."""

        list_config = source_list.list_config or {}
        if source_list.list_type == "label":
            lid = _get_uuid_from_config(list_config, "label_id")
            if lid and await self._label_repository.issue_has_label(issue.id, lid):
                await self._label_repository.remove_label_from_issue(issue.id, lid)
        elif source_list.list_type == "assignee":
            issue.update_assignee(None)
            await self._issue_repository.update(issue)
        elif source_list.list_type == "milestone":
            sid = _get_uuid_from_config(list_config, "sprint_id")
            if sid:
                try:
                    await self._sprint_repository.remove_issue_from_sprint(sid, issue.id)
                except EntityNotFoundException:
                    pass

    async def _apply_target_list_actions(
        self,
        issue: Issue,
        target_list: BoardList,
        project_id: UUID,
    ) -> None:
        """Add label / set assignee / add to sprint for target list."""
        list_config = target_list.list_config or {}
        if target_list.list_type == "label":
            lid = _get_uuid_from_config(list_config, "label_id")
            if lid:
                try:
                    await self._label_repository.add_label_to_issue(issue.id, lid)
                except ConflictException:
                    pass
        elif target_list.list_type == "assignee":
            uid = _get_uuid_from_config(list_config, "user_id")
            if uid:
                issue.update_assignee(uid)
                await self._issue_repository.update(issue)
        elif target_list.list_type == "milestone":
            sid = _get_uuid_from_config(list_config, "sprint_id")
            if sid:
                issues_in_sprint = await self._sprint_repository.get_sprint_issues(sid)
                order = (
                    (max((o for _, o in issues_in_sprint), default=-1) + 1)
                    if issues_in_sprint
                    else 0
                )
                try:
                    await self._sprint_repository.add_issue_to_sprint(sid, issue.id, order)
                except ConflictException:
                    pass

    async def _build_issue_response(
        self, issue: Issue, project_key: str, project_id: UUID
    ) -> BoardIssueItemResponse:
        """Build BoardIssueItemResponse for an issue."""

        labels = await self._label_repository.get_labels_for_issue(issue.id)
        label_ids = [lab.id for lab in labels]
        comment_count = await self._comment_repository.count_by_issue_id(issue.id)
        subtask_count = await self._issue_repository.count(project_id, parent_issue_id=issue.id)
        return BoardIssueItemResponse(
            id=issue.id,
            issue_number=issue.issue_number,
            key=issue.generate_key(project_key),
            project_id=project_id,
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


def _get_uuid_from_config(config: dict, key: str) -> UUID | None:
    """Extract UUID from list_config value (may be UUID or str)."""
    v = config.get(key)
    if v is None:
        return None
    if isinstance(v, UUID):
        return v
    try:
        return UUID(str(v))
    except (ValueError, TypeError):
        return None


def _extract_label_ids(value: object) -> list[UUID]:
    """Extract list of UUIDs from scope_config label_ids."""
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
