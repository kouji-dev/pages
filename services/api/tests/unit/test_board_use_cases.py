"""Unit tests for board use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.board import (
    CreateBoardListRequest,
    CreateBoardRequest,
    UpdateBoardListRequest,
    UpdateBoardRequest,
)
from src.application.use_cases.board import (
    CreateBoardListUseCase,
    CreateBoardUseCase,
    DeleteBoardListUseCase,
    DeleteBoardUseCase,
    GetBoardIssuesUseCase,
    GetBoardUseCase,
    ListBoardListsUseCase,
    ListProjectBoardsUseCase,
    MoveBoardIssueUseCase,
    UpdateBoardListUseCase,
    UpdateBoardUseCase,
)
from src.domain.entities import Board, Project
from src.domain.entities.board import BoardList
from src.domain.exceptions import ConflictException, EntityNotFoundException


@pytest.fixture
def mock_board_repository():
    """Mock board repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
    )


@pytest.fixture
def test_board(test_project):
    """Create a test board."""
    return Board.create(
        project_id=test_project.id,
        name="Backlog",
        description="Backlog board",
        position=0,
        is_default=True,
    )


class TestCreateBoardUseCase:
    """Tests for CreateBoardUseCase."""

    @pytest.mark.asyncio
    async def test_create_board_success(
        self, mock_board_repository, mock_project_repository, test_project
    ):
        """Test successful board creation (first board -> default)."""
        request = CreateBoardRequest(name="Backlog", description="Backlog board")
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.count_by_project.return_value = 0
        created = Board.create(
            project_id=test_project.id,
            name=request.name,
            description=request.description,
            is_default=True,
        )
        mock_board_repository.create.return_value = created

        use_case = CreateBoardUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, request)

        assert result.name == "Backlog"
        assert result.is_default is True
        mock_board_repository.create.assert_called_once()
        mock_board_repository.set_default_board.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_board_second_board_with_default(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test creating second board with is_default=True calls set_default_board."""
        request = CreateBoardRequest(name="Sprint", is_default=True)
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.count_by_project.return_value = 1
        new_board = Board.create(
            project_id=test_project.id,
            name=request.name,
            is_default=True,
        )
        new_board.id = uuid4()
        mock_board_repository.create.return_value = new_board

        use_case = CreateBoardUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, request, created_by=uuid4())

        assert result.name == "Sprint"
        mock_board_repository.set_default_board.assert_called_once_with(
            test_project.id, new_board.id
        )

    @pytest.mark.asyncio
    async def test_create_board_project_not_found(
        self, mock_board_repository, mock_project_repository
    ):
        """Test board creation when project not found."""
        mock_project_repository.get_by_id.return_value = None
        request = CreateBoardRequest(name="Backlog")

        use_case = CreateBoardUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(uuid4(), request)


class TestGetBoardUseCase:
    """Tests for GetBoardUseCase."""

    @pytest.mark.asyncio
    async def test_get_board_success(self, mock_board_repository, test_board):
        """Test successful board retrieval with lists."""
        mock_board_repository.get_by_id_with_lists.return_value = (test_board, [])

        use_case = GetBoardUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id)

        assert result.id == test_board.id
        assert result.name == test_board.name
        assert result.lists == []

    @pytest.mark.asyncio
    async def test_get_board_not_found(self, mock_board_repository):
        """Test get board when not found."""
        mock_board_repository.get_by_id_with_lists.return_value = None

        use_case = GetBoardUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())


class TestListProjectBoardsUseCase:
    """Tests for ListProjectBoardsUseCase."""

    @pytest.mark.asyncio
    async def test_list_boards_success(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test successful board listing."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_project.return_value = [test_board]
        mock_board_repository.count_by_project.return_value = 1

        use_case = ListProjectBoardsUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, page=1, limit=20)

        assert result.total == 1
        assert len(result.boards) == 1
        assert result.boards[0].name == test_board.name
        assert result.page == 1
        assert result.limit == 20
        assert result.pages == 1

    @pytest.mark.asyncio
    async def test_list_boards_project_not_found(
        self, mock_board_repository, mock_project_repository
    ):
        """Test list boards when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = ListProjectBoardsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_list_boards_pagination(
        self, mock_board_repository, mock_project_repository, test_project
    ):
        """Test list boards pagination."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_project.return_value = []
        mock_board_repository.count_by_project.return_value = 50

        use_case = ListProjectBoardsUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, page=2, limit=10)

        assert result.total == 50
        assert result.page == 2
        assert result.limit == 10
        assert result.pages == 5
        mock_board_repository.get_by_project.assert_called_once_with(
            project_id=test_project.id, skip=10, limit=10
        )


class TestUpdateBoardUseCase:
    """Tests for UpdateBoardUseCase."""

    @pytest.mark.asyncio
    async def test_update_board_success(self, mock_board_repository, test_board):
        """Test successful board update."""
        request = UpdateBoardRequest(name="Updated Name", description="New desc")
        mock_board_repository.get_by_id.return_value = test_board
        updated = Board(
            id=test_board.id,
            project_id=test_board.project_id,
            name="Updated Name",
            description="New desc",
            scope_config=test_board.scope_config,
            is_default=test_board.is_default,
            position=test_board.position,
            created_by=test_board.created_by,
            created_at=test_board.created_at,
            updated_at=test_board.updated_at,
        )
        mock_board_repository.update.return_value = updated

        use_case = UpdateBoardUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, request)

        assert result.name == "Updated Name"
        assert result.description == "New desc"
        mock_board_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_board_scope_config(self, mock_board_repository, test_board):
        """Test update board scope_config."""
        request = UpdateBoardRequest(scope_config={"label_ids": [str(uuid4())]})
        mock_board_repository.get_by_id.return_value = test_board
        test_board.update_scope_config(request.scope_config)
        mock_board_repository.update.return_value = test_board

        use_case = UpdateBoardUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, request)

        assert result.scope_config == request.scope_config

    @pytest.mark.asyncio
    async def test_update_board_position(self, mock_board_repository, test_board):
        """Test update board position."""
        request = UpdateBoardRequest(position=2)
        mock_board_repository.get_by_id.return_value = test_board
        test_board.update_position(2)
        mock_board_repository.update.return_value = test_board

        use_case = UpdateBoardUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, request)

        assert result.position == 2

    @pytest.mark.asyncio
    async def test_update_board_not_found(self, mock_board_repository):
        """Test update board when not found."""
        mock_board_repository.get_by_id.return_value = None
        request = UpdateBoardRequest(name="Updated")

        use_case = UpdateBoardUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), request)


class TestDeleteBoardUseCase:
    """Tests for DeleteBoardUseCase."""

    @pytest.mark.asyncio
    async def test_delete_board_success(self, mock_board_repository, test_project, test_board):
        """Test successful board deletion."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.count_by_project.return_value = 2

        use_case = DeleteBoardUseCase(mock_board_repository)
        await use_case.execute(test_board.id)

        mock_board_repository.delete.assert_called_once_with(test_board.id)

    @pytest.mark.asyncio
    async def test_delete_board_not_found(self, mock_board_repository):
        """Test delete board when not found."""
        mock_board_repository.get_by_id.return_value = None

        use_case = DeleteBoardUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_delete_board_last_board_raises_conflict(self, mock_board_repository, test_board):
        """Test cannot delete last board of project."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.count_by_project.return_value = 1

        use_case = DeleteBoardUseCase(mock_board_repository)
        with pytest.raises(ConflictException, match="last board"):
            await use_case.execute(test_board.id)

        mock_board_repository.delete.assert_not_called()


# --- Board List (Column) use cases ---


class TestCreateBoardListUseCase:
    """Tests for CreateBoardListUseCase."""

    @pytest.mark.asyncio
    async def test_create_board_list_success(self, mock_board_repository, test_board):
        """Test successful board list creation (position = max+1)."""
        request = CreateBoardListRequest(list_type="label", list_config={"label_id": str(uuid4())})
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_max_list_position.return_value = 0
        created_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config=request.list_config,
            position=1,
        )
        mock_board_repository.create_board_list.return_value = created_list

        use_case = CreateBoardListUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, request)

        assert result.list_type == "label"
        assert result.position == 1
        mock_board_repository.get_max_list_position.assert_called_once_with(test_board.id)
        mock_board_repository.create_board_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_board_list_board_not_found(self, mock_board_repository):
        """Test create list when board not found."""
        mock_board_repository.get_by_id.return_value = None
        request = CreateBoardListRequest(
            list_type="assignee", list_config={"user_id": str(uuid4())}
        )

        use_case = CreateBoardListUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), request)


class TestUpdateBoardListUseCase:
    """Tests for UpdateBoardListUseCase."""

    @pytest.mark.asyncio
    async def test_update_board_list_position(self, mock_board_repository, test_board):
        """Test update board list position."""
        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        mock_board_repository.get_board_list_by_id.return_value = board_list
        board_list.update_position(1)
        mock_board_repository.update_board_list.return_value = board_list

        request = UpdateBoardListRequest(position=1)
        use_case = UpdateBoardListUseCase(mock_board_repository)
        result = await use_case.execute(board_list.id, request)

        assert result.position == 1
        mock_board_repository.update_board_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_board_list_config_only(self, mock_board_repository, test_board):
        """Test update board list list_config only (position unchanged)."""
        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        mock_board_repository.get_board_list_by_id.return_value = board_list
        board_list.update_list_config({"label_id": str(uuid4())})
        mock_board_repository.update_board_list.return_value = board_list

        request = UpdateBoardListRequest(list_config={"label_id": str(uuid4())})
        use_case = UpdateBoardListUseCase(mock_board_repository)
        result = await use_case.execute(board_list.id, request)

        assert result.list_config == request.list_config
        mock_board_repository.update_board_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_board_list_not_found(self, mock_board_repository):
        """Test update list when not found."""
        mock_board_repository.get_board_list_by_id.return_value = None
        request = UpdateBoardListRequest(position=2)

        use_case = UpdateBoardListUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="BoardList"):
            await use_case.execute(uuid4(), request)


class TestDeleteBoardListUseCase:
    """Tests for DeleteBoardListUseCase."""

    @pytest.mark.asyncio
    async def test_delete_board_list_success(self, mock_board_repository, test_board):
        """Test successful board list deletion."""
        board_list = BoardList.create(board_id=test_board.id, list_type="label", position=0)
        mock_board_repository.get_board_list_by_id.return_value = board_list

        use_case = DeleteBoardListUseCase(mock_board_repository)
        await use_case.execute(board_list.id)

        mock_board_repository.delete_board_list.assert_called_once_with(board_list.id)

    @pytest.mark.asyncio
    async def test_delete_board_list_not_found(self, mock_board_repository):
        """Test delete list when not found."""
        mock_board_repository.get_board_list_by_id.return_value = None

        use_case = DeleteBoardListUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="BoardList"):
            await use_case.execute(uuid4())


class TestListBoardListsUseCase:
    """Tests for ListBoardListsUseCase."""

    @pytest.mark.asyncio
    async def test_list_board_lists_success(self, mock_board_repository, test_board):
        """Test list board lists ordered by position."""
        board_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(uuid4())},
            position=0,
        )
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]

        use_case = ListBoardListsUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id)

        assert result.total == 1
        assert len(result.lists) == 1
        assert result.lists[0].list_type == "label"

    @pytest.mark.asyncio
    async def test_list_board_lists_board_not_found(self, mock_board_repository):
        """Test list lists when board not found."""
        mock_board_repository.get_by_id.return_value = None

        use_case = ListBoardListsUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())


class TestGetBoardIssuesUseCase:
    """Tests for GetBoardIssuesUseCase."""

    @pytest.fixture
    def mock_issue_repository(self):
        """Mock issue repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_label_repository(self):
        """Mock label repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_comment_repository(self):
        """Mock comment repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository_for_issues(self):
        """Mock project repository with key."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_board_issues_success(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test get board issues returns lists with issues."""
        board_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(uuid4())},
            position=0,
        )
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = []
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 1
        assert result.lists[0].id == board_list.id
        assert result.lists[0].issues == []

    @pytest.mark.asyncio
    async def test_get_board_issues_board_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
    ):
        """Test get board issues when board not found."""
        mock_board_repository.get_by_id.return_value = None

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
        )
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_get_board_issues_project_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
    ):
        """Test get board issues when project not found."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = None

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
        )
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(test_board.id)

    @pytest.mark.asyncio
    async def test_get_board_issues_with_issues_in_list(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test get board issues when a list has issues (covers item build and scope filter)."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        issue = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Task",
        )
        scope_label_id = uuid4()
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [issue]
        mock_label_repository.get_labels_for_issue.return_value = (
            []
        )  # no labels -> filtered if scope
        mock_comment_repository.count_by_issue_id.return_value = 2
        mock_issue_repository.count.return_value = 0

        # No scope: issue is included
        test_board.scope_config = None
        mock_board_repository.get_by_id.return_value = test_board
        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
        )
        result = await use_case.execute(test_board.id)
        assert len(result.lists) == 1
        assert len(result.lists[0].issues) == 1
        assert result.lists[0].issues[0].title == "Task"
        assert result.lists[0].issues[0].comment_count == 2

        # With scope and issue has no matching label: issue filtered out
        test_board.scope_config = {"label_ids": [str(scope_label_id)]}
        mock_board_repository.get_by_id.return_value = test_board
        result2 = await use_case.execute(test_board.id)
        assert len(result2.lists[0].issues) == 0

    @pytest.mark.asyncio
    async def test_get_board_issues_assignee_and_milestone_lists(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test _load_issues_for_list with assignee and milestone list types."""
        user_id = uuid4()
        sprint_id = uuid4()
        list_assignee = BoardList.create(
            board_id=test_board.id,
            list_type="assignee",
            list_config={"user_id": str(user_id)},
            position=0,
        )
        list_milestone = BoardList.create(
            board_id=test_board.id,
            list_type="milestone",
            list_config={"sprint_id": str(sprint_id)},
            position=1,
        )
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [
            list_assignee,
            list_milestone,
        ]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = []

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 2
        call_kw = mock_issue_repository.get_all.call_args_list[0].kwargs
        assert call_kw.get("assignee_id") == user_id
        call_kw2 = mock_issue_repository.get_all.call_args_list[1].kwargs
        assert call_kw2.get("sprint_id") == sprint_id


def test_extract_label_ids():
    """Test _extract_label_ids for scope_config label_ids (UUID, str, invalid)."""
    from src.application.use_cases.board.get_board_issues import _extract_label_ids

    assert _extract_label_ids(None) == []
    assert _extract_label_ids([]) == []
    assert _extract_label_ids("not a list") == []
    u = uuid4()
    assert _extract_label_ids([u]) == [u]
    assert _extract_label_ids([str(u)]) == [u]
    assert _extract_label_ids([u, str(uuid4())])  # mixed, length 2
    # invalid str is skipped
    assert _extract_label_ids(["not-a-uuid"]) == []
    assert _extract_label_ids([u, "bad", str(u)]) == [u, u]


# --- Move Board Issue (Drag & Drop) ---


class TestMoveBoardIssueUseCase:
    """Tests for MoveBoardIssueUseCase (2.5.7 drag & drop with label swapping)."""

    @pytest.fixture
    def mock_issue_repository(self):
        """Mock issue repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_label_repository(self):
        """Mock label repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_comment_repository(self):
        """Mock comment repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_sprint_repository(self):
        """Mock sprint repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository_for_issues(self):
        """Mock project repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_issue_activity_repository(self):
        """Mock issue activity repository."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_move_same_column_no_op(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when source_list_id == target_list_id returns issue without applying changes."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        list_id = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        source_list.id = list_id

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.return_value = source_list

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(test_board.id, issue.id, list_id, list_id, user_id=uuid4())

        assert result.id == issue.id
        assert result.title == "Task"
        mock_issue_activity_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_board_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
    ):
        """Test move when board not found."""
        mock_board_repository.get_by_id.return_value = None
        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), uuid4(), uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_issue_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when issue not found."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = None
        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(test_board.id, uuid4(), uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_source_list_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when source list not found."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_board_repository.get_board_list_by_id.return_value = None

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="BoardList"):
            await use_case.execute(test_board.id, issue.id, uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_label_swap_success(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move from label list to another label list (remove source label, add target label)."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        label_src = uuid4()
        label_tgt = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(label_src)},
            position=0,
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(label_tgt)},
            position=1,
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_label_repository.issue_has_label.return_value = True
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )

        assert result.id == issue.id
        mock_label_repository.remove_label_from_issue.assert_called_once_with(issue.id, label_src)
        mock_label_repository.add_label_to_issue.assert_called_once_with(issue.id, label_tgt)
        mock_issue_activity_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_assignee_swap_success(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move from assignee list to another (clear assignee, set new assignee)."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        user_tgt = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id, list_type="assignee", list_config={}, position=0
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id,
            list_type="assignee",
            list_config={"user_id": str(user_tgt)},
            position=1,
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )

        assert result.id == issue.id
        mock_issue_repository.update.assert_called()
        mock_issue_activity_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_issue_not_in_scope_raises(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when board has scope_config and issue has no matching label."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        test_board.scope_config = {"label_ids": [str(uuid4())]}
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(test_board.id, issue.id, uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_project_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
    ):
        """Test move when project not found."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = None
        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(test_board.id, uuid4(), uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_issue_wrong_project(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when issue belongs to another project."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=uuid4(), issue_number=1, title="Task")
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(test_board.id, issue.id, uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_move_target_list_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when target list not found."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        source_list = BoardList.create(board_id=test_board.id, list_type="label", position=0)
        source_list.id = uuid4()
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, None]
        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="BoardList"):
            await use_case.execute(test_board.id, issue.id, source_list.id, uuid4())

    @pytest.mark.asyncio
    async def test_move_milestone_swap_success(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move from milestone list to another (remove from source sprint, add to target)."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        sprint_src = uuid4()
        sprint_tgt = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id,
            list_type="milestone",
            list_config={"sprint_id": str(sprint_src)},
            position=0,
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id,
            list_type="milestone",
            list_config={"sprint_id": str(sprint_tgt)},
            position=1,
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]
        mock_sprint_repository.get_sprint_issues.return_value = [(uuid4(), 0)]

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )

        assert result.id == issue.id
        mock_sprint_repository.remove_issue_from_sprint.assert_called_once_with(
            sprint_src, issue.id
        )
        mock_sprint_repository.add_issue_to_sprint.assert_called_once_with(sprint_tgt, issue.id, 1)
        mock_issue_activity_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_label_target_already_has_conflict(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move to label list when issue already has that label (ConflictException ignored)."""
        from src.domain.entities import Issue
        from src.domain.exceptions import ConflictException

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        label_tgt = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(label_tgt)},
            position=1,
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_label_repository.add_label_to_issue.side_effect = ConflictException(
            "already has label"
        )
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )
        assert result.id == issue.id
        mock_issue_activity_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_source_milestone_remove_not_found(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move from milestone list when issue not in sprint (EntityNotFoundException caught)."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        sprint_src = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=1
        )
        target_list.id = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id,
            list_type="milestone",
            list_config={"sprint_id": str(sprint_src)},
            position=0,
        )
        source_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]
        mock_sprint_repository.remove_issue_from_sprint.side_effect = EntityNotFoundException(
            "SprintIssue", "x"
        )

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )
        assert result.id == issue.id

    @pytest.mark.asyncio
    async def test_move_target_milestone_already_in_sprint(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move to milestone list when issue already in sprint (ConflictException caught)."""
        from src.domain.entities import Issue
        from src.domain.exceptions import ConflictException

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        sprint_tgt = uuid4()
        source_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id,
            list_type="milestone",
            list_config={"sprint_id": str(sprint_tgt)},
            position=1,
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]
        mock_sprint_repository.get_sprint_issues.return_value = []
        mock_sprint_repository.add_issue_to_sprint.side_effect = ConflictException(
            "already in sprint"
        )

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        result = await use_case.execute(
            test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
        )
        assert result.id == issue.id

    @pytest.mark.asyncio
    async def test_move_updated_issue_not_found_raises(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_sprint_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        mock_issue_activity_repository,
        test_board,
        test_project,
    ):
        """Test move when re-fetch of issue after apply returns None (94)."""
        from src.domain.entities import Issue

        issue = Issue.create(project_id=test_board.project_id, issue_number=1, title="Task")
        source_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        source_list.id = uuid4()
        target_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=1
        )
        target_list.id = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_by_id.side_effect = [issue, None]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_board_repository.get_board_list_by_id.side_effect = [source_list, target_list]

        use_case = MoveBoardIssueUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_sprint_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_issue_activity_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(
                test_board.id, issue.id, source_list.id, target_list.id, user_id=uuid4()
            )


def test_get_uuid_from_config():
    """Test _get_uuid_from_config in move_board_issue."""
    from src.application.use_cases.board.move_board_issue import _get_uuid_from_config

    assert _get_uuid_from_config({}, "label_id") is None
    assert _get_uuid_from_config({"label_id": None}, "label_id") is None
    u = uuid4()
    assert _get_uuid_from_config({"label_id": u}, "label_id") == u
    assert _get_uuid_from_config({"label_id": str(u)}, "label_id") == u
    assert _get_uuid_from_config({"label_id": "not-uuid"}, "label_id") is None
    # invalid str triggers ValueError in UUID(str(v))
    assert _get_uuid_from_config({"label_id": ""}, "label_id") is None


def test_extract_label_ids_move_board_issue():
    """Test _extract_label_ids in move_board_issue (covers str branch and except)."""
    from src.application.use_cases.board.move_board_issue import _extract_label_ids

    u = uuid4()
    assert _extract_label_ids([u]) == [u]
    assert _extract_label_ids([str(u)]) == [u]
    assert _extract_label_ids(["invalid-uuid"]) == []
    assert _extract_label_ids([str(u), "bad"]) == [u]
