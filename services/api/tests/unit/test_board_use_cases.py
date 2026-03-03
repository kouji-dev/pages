"""Unit tests for board use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.board import (
    CreateBoardListRequest,
    CreateBoardRequest,
    CreateGroupBoardRequest,
    UpdateBoardListRequest,
    UpdateBoardRequest,
    UpdateBoardScopeRequest,
)
from src.application.use_cases.board import (
    CreateBoardListUseCase,
    CreateBoardUseCase,
    CreateGroupBoardUseCase,
    DeleteBoardListUseCase,
    DeleteBoardUseCase,
    DuplicateBoardUseCase,
    GetBoardIssuesUseCase,
    GetBoardUseCase,
    ListBoardListsUseCase,
    ListProjectBoardsUseCase,
    MoveBoardIssueUseCase,
    ReorderBoardsUseCase,
    SetDefaultBoardUseCase,
    SetGroupBoardProjectsUseCase,
    UpdateBoardListUseCase,
    UpdateBoardScopeUseCase,
    UpdateBoardSwimlanesUseCase,
    UpdateBoardUseCase,
)
from src.domain.entities import Board, Project
from src.domain.entities.board import BoardList
from src.domain.exceptions import ConflictException, EntityNotFoundException, ValidationException


@pytest.fixture
def mock_board_repository():
    """Mock board repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_organization_repository():
    """Mock organization repository."""
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


class TestCreateGroupBoardUseCase:
    """Tests for CreateGroupBoardUseCase (Phase 2.5.17)."""

    @pytest.mark.asyncio
    async def test_create_group_board_success(
        self,
        mock_board_repository,
        mock_organization_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful group board creation with multiple projects."""
        org_id = test_project.organization_id
        request = CreateGroupBoardRequest(
            name="Group Board",
            description="Org board",
            project_ids=[test_project.id],
        )
        mock_organization_repository.get_by_id.return_value = type("Org", (), {"id": org_id})()
        mock_project_repository.get_by_id.return_value = test_project
        group_board = Board.create_group(
            organization_id=org_id,
            primary_project_id=test_project.id,
            name=request.name,
            description=request.description,
        )
        mock_board_repository.create.return_value = group_board
        mock_board_repository.set_projects_for_group_board.return_value = None

        use_case = CreateGroupBoardUseCase(
            mock_board_repository,
            mock_organization_repository,
            mock_project_repository,
        )
        result = await use_case.execute(org_id, request, created_by=uuid4())

        assert result.name == "Group Board"
        assert result.board_type == "group"
        assert result.organization_id == org_id
        mock_board_repository.set_projects_for_group_board.assert_called_once_with(
            group_board.id, [test_project.id]
        )

    @pytest.mark.asyncio
    async def test_create_group_board_organization_not_found(
        self,
        mock_board_repository,
        mock_organization_repository,
        mock_project_repository,
    ):
        """Test group board creation when organization not found."""
        mock_organization_repository.get_by_id.return_value = None
        request = CreateGroupBoardRequest(name="GB", project_ids=[uuid4()])
        use_case = CreateGroupBoardUseCase(
            mock_board_repository,
            mock_organization_repository,
            mock_project_repository,
        )
        with pytest.raises(EntityNotFoundException, match="Organization"):
            await use_case.execute(uuid4(), request)

    @pytest.mark.asyncio
    async def test_create_group_board_project_not_in_org(
        self,
        mock_board_repository,
        mock_organization_repository,
        mock_project_repository,
        test_project,
    ):
        """Test group board when a project belongs to another organization."""
        org_id = uuid4()
        other_org_id = uuid4()
        mock_organization_repository.get_by_id.return_value = type("Org", (), {"id": org_id})()
        # Project belongs to other_org_id
        proj = Project.create(organization_id=other_org_id, name="P", key="P")
        mock_project_repository.get_by_id.return_value = proj
        request = CreateGroupBoardRequest(name="GB", project_ids=[proj.id])
        use_case = CreateGroupBoardUseCase(
            mock_board_repository,
            mock_organization_repository,
            mock_project_repository,
        )
        with pytest.raises(ValidationException, match="same organization"):
            await use_case.execute(org_id, request)


class TestSetGroupBoardProjectsUseCase:
    """Tests for SetGroupBoardProjectsUseCase (Phase 2.5.17)."""

    @pytest.mark.asyncio
    async def test_set_projects_success(
        self, mock_board_repository, mock_project_repository, test_project
    ):
        """Test setting projects on a group board."""
        group_board = Board(
            id=uuid4(),
            project_id=test_project.id,
            name="GB",
            description=None,
            scope_config=None,
            is_default=False,
            position=0,
            created_by=None,
            organization_id=test_project.organization_id,
            board_type="group",
            created_at=test_project.created_at,
            updated_at=test_project.updated_at,
        )
        mock_board_repository.get_by_id.return_value = group_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.set_projects_for_group_board.return_value = None

        use_case = SetGroupBoardProjectsUseCase(mock_board_repository, mock_project_repository)
        await use_case.execute(group_board.id, [test_project.id])

        mock_board_repository.set_projects_for_group_board.assert_called_once_with(
            group_board.id, [test_project.id]
        )

    @pytest.mark.asyncio
    async def test_set_projects_board_not_found(
        self, mock_board_repository, mock_project_repository
    ):
        """Test set projects when board not found."""
        mock_board_repository.get_by_id.return_value = None
        use_case = SetGroupBoardProjectsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), [uuid4()])

    @pytest.mark.asyncio
    async def test_set_projects_not_group_board(
        self, mock_board_repository, mock_project_repository, test_board
    ):
        """Test set projects when board is project type."""
        mock_board_repository.get_by_id.return_value = test_board
        use_case = SetGroupBoardProjectsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException, match="group boards"):
            await use_case.execute(test_board.id, [test_board.project_id])

    @pytest.mark.asyncio
    async def test_set_projects_empty_list(
        self, mock_board_repository, mock_project_repository, test_project
    ):
        """Test set projects with empty list raises ValidationException."""
        group_board = Board(
            id=uuid4(),
            project_id=test_project.id,
            name="GB",
            description=None,
            scope_config=None,
            is_default=False,
            position=0,
            created_by=None,
            organization_id=test_project.organization_id,
            board_type="group",
            created_at=test_project.created_at,
            updated_at=test_project.updated_at,
        )
        mock_board_repository.get_by_id.return_value = group_board
        use_case = SetGroupBoardProjectsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException, match="at least one"):
            await use_case.execute(group_board.id, [])


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
            project_id=test_project.id, skip=10, limit=10, search=None
        )
        mock_board_repository.count_by_project.assert_called_once_with(test_project.id, search=None)

    @pytest.mark.asyncio
    async def test_list_boards_with_search(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test list boards with search by name."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_project.return_value = [test_board]
        mock_board_repository.count_by_project.return_value = 1

        use_case = ListProjectBoardsUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, page=1, limit=20, search="Backlog")

        assert result.total == 1
        mock_board_repository.get_by_project.assert_called_once_with(
            project_id=test_project.id, skip=0, limit=20, search="Backlog"
        )
        mock_board_repository.count_by_project.assert_called_once_with(
            test_project.id, search="Backlog"
        )


class TestSetDefaultBoardUseCase:
    """Tests for SetDefaultBoardUseCase."""

    @pytest.mark.asyncio
    async def test_set_default_board_success(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test setting a board as default."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        updated = Board(
            id=test_board.id,
            project_id=test_board.project_id,
            name=test_board.name,
            description=test_board.description,
            scope_config=test_board.scope_config,
            is_default=True,
            position=test_board.position,
            created_by=test_board.created_by,
            created_at=test_board.created_at,
            updated_at=test_board.updated_at,
        )
        mock_board_repository.get_by_id.side_effect = [test_board, updated]

        use_case = SetDefaultBoardUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_board.id)

        assert result.is_default is True
        mock_board_repository.set_default_board.assert_called_once_with(
            test_project.id, test_board.id
        )

    @pytest.mark.asyncio
    async def test_set_default_board_not_found(
        self, mock_board_repository, mock_project_repository
    ):
        """Test set default when board not found."""
        mock_board_repository.get_by_id.return_value = None

        use_case = SetDefaultBoardUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_set_default_board_project_not_found(
        self, mock_board_repository, mock_project_repository, test_board
    ):
        """Test set default when project not found."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = None

        use_case = SetDefaultBoardUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(test_board.id)

    @pytest.mark.asyncio
    async def test_set_default_board_reload_returns_none(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test set default when re-fetching board after set_default returns None."""
        mock_board_repository.get_by_id.side_effect = [test_board, None]
        mock_project_repository.get_by_id.return_value = test_project

        use_case = SetDefaultBoardUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(test_board.id)


class TestDuplicateBoardUseCase:
    """Tests for DuplicateBoardUseCase."""

    @pytest.mark.asyncio
    async def test_duplicate_board_success(self, mock_board_repository, test_board, test_project):
        """Test duplicating a board with lists."""
        from src.domain.entities.board import BoardList

        list1 = BoardList(
            id=uuid4(),
            board_id=test_board.id,
            list_type="label",
            list_config={"label_id": str(uuid4())},
            position=0,
        )
        mock_board_repository.get_by_id_with_lists.return_value = (test_board, [list1])
        mock_board_repository.count_by_project.return_value = 1
        new_board = Board.create(
            project_id=test_board.project_id,
            name="Copy of Backlog",
            description=test_board.description,
            is_default=False,
            position=1,
        )
        new_board.id = uuid4()
        new_list = BoardList.create(
            board_id=new_board.id,
            list_type="label",
            list_config=list1.list_config,
            position=0,
        )
        mock_board_repository.create.return_value = new_board
        mock_board_repository.create_board_list.return_value = new_list

        use_case = DuplicateBoardUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id)

        assert result.name == "Copy of Backlog"
        assert result.is_default is False
        assert len(result.lists) == 1
        assert result.lists[0].list_type == "label"
        mock_board_repository.create.assert_called_once()
        mock_board_repository.create_board_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_board_not_found(self, mock_board_repository):
        """Test duplicate when board not found."""
        mock_board_repository.get_by_id_with_lists.return_value = None

        use_case = DuplicateBoardUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4())


class TestReorderBoardsUseCase:
    """Tests for ReorderBoardsUseCase."""

    @pytest.mark.asyncio
    async def test_reorder_boards_success(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test reordering boards."""
        board2 = Board.create(
            project_id=test_project.id,
            name="Sprint",
            position=1,
        )
        board2.id = uuid4()
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_id.side_effect = [test_board, board2]

        use_case = ReorderBoardsUseCase(mock_board_repository, mock_project_repository)
        await use_case.execute(test_project.id, [board2.id, test_board.id])

        mock_board_repository.reorder_boards.assert_called_once_with(
            test_project.id, [board2.id, test_board.id]
        )

    @pytest.mark.asyncio
    async def test_reorder_boards_project_not_found(
        self, mock_board_repository, mock_project_repository
    ):
        """Test reorder when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = ReorderBoardsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(uuid4(), [uuid4()])

    @pytest.mark.asyncio
    async def test_reorder_boards_board_not_found(
        self, mock_board_repository, mock_project_repository, test_project
    ):
        """Test reorder when one board not found."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_id.return_value = None

        use_case = ReorderBoardsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(test_project.id, [uuid4()])

    @pytest.mark.asyncio
    async def test_reorder_boards_board_from_other_project(
        self, mock_board_repository, mock_project_repository, test_project, test_board
    ):
        """Test reorder when board belongs to another project."""
        other_board = Board.create(
            project_id=uuid4(),
            name="Other",
            position=0,
        )
        other_board.id = uuid4()
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_by_id.side_effect = [test_board, other_board]

        use_case = ReorderBoardsUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(test_project.id, [test_board.id, other_board.id])


class TestUpdateBoardScopeUseCase:
    """Tests for UpdateBoardScopeUseCase."""

    @pytest.mark.asyncio
    async def test_update_board_scope_success(
        self,
        mock_board_repository,
        mock_project_repository,
        test_project,
        test_board,
    ):
        """Test successful update of board scope_config."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_lists_for_board.return_value = []
        updated_board = Board(
            id=test_board.id,
            project_id=test_board.project_id,
            name=test_board.name,
            description=test_board.description,
            scope_config={
                "label_ids": [],
                "assignee_id": None,
                "types": ["task"],
                "priorities": ["medium"],
            },
            is_default=test_board.is_default,
            position=test_board.position,
            created_by=test_board.created_by,
            created_at=test_board.created_at,
            updated_at=test_board.updated_at,
        )
        mock_board_repository.update.return_value = updated_board

        request = UpdateBoardScopeRequest(
            label_ids=[],
            assignee_id=None,
            milestone_id=None,
            types=["task"],
            priorities=["medium"],
        )

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        result = await use_case.execute(test_board.id, request)

        assert result.scope_config["types"] == ["task"]
        assert result.scope_config["priorities"] == ["medium"]
        mock_board_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_board_scope_board_not_found(
        self,
        mock_board_repository,
        mock_project_repository,
    ):
        """Test update scope when board not found."""
        mock_board_repository.get_by_id.return_value = None
        request = UpdateBoardScopeRequest()

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), request)

    @pytest.mark.asyncio
    async def test_update_board_scope_project_not_found(
        self,
        mock_board_repository,
        mock_project_repository,
        test_board,
    ):
        """Test update scope when project not found."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = None
        request = UpdateBoardScopeRequest()

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(test_board.id, request)

    @pytest.mark.asyncio
    async def test_update_board_scope_label_overlap_validation(
        self,
        mock_board_repository,
        mock_project_repository,
        test_project,
        test_board,
    ):
        """Test validation error when label_ids and exclude_label_ids overlap."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_lists_for_board.return_value = []
        lid = uuid4()
        request = UpdateBoardScopeRequest(label_ids=[lid], exclude_label_ids=[lid])

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException):
            await use_case.execute(test_board.id, request)

    @pytest.mark.asyncio
    async def test_update_board_scope_fixed_user_conflict_with_lists(
        self,
        mock_board_repository,
        mock_project_repository,
        test_project,
        test_board,
    ):
        """Test validation error when fixed_user_id conflicts with assignee lists."""
        from src.domain.entities.board import BoardList

        user1 = uuid4()
        user2 = uuid4()
        list_assignee = BoardList.create(
            board_id=test_board.id,
            list_type="assignee",
            list_config={"user_id": str(user1)},
            position=0,
        )
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_lists_for_board.return_value = [list_assignee]

        request = UpdateBoardScopeRequest(fixed_user_id=user2)

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException):
            await use_case.execute(test_board.id, request)

    @pytest.mark.asyncio
    async def test_update_board_scope_assignee_and_fixed_user_mismatch(
        self,
        mock_board_repository,
        mock_project_repository,
        test_project,
        test_board,
    ):
        """Test validation error when assignee_id and fixed_user_id differ."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_lists_for_board.return_value = []

        request = UpdateBoardScopeRequest(
            assignee_id=uuid4(),
            fixed_user_id=uuid4(),
        )

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException):
            await use_case.execute(test_board.id, request)

    @pytest.mark.asyncio
    async def test_update_board_scope_story_points_range_invalid(
        self,
        mock_board_repository,
        mock_project_repository,
        test_project,
        test_board,
    ):
        """Test validation error when story_points_min > story_points_max."""
        mock_board_repository.get_by_id.return_value = test_board
        mock_project_repository.get_by_id.return_value = test_project
        mock_board_repository.get_lists_for_board.return_value = []

        request = UpdateBoardScopeRequest(story_points_min=5, story_points_max=3)

        use_case = UpdateBoardScopeUseCase(mock_board_repository, mock_project_repository)
        with pytest.raises(ValidationException):
            await use_case.execute(test_board.id, request)


class TestUpdateBoardSwimlanesUseCase:
    """Tests for UpdateBoardSwimlanesUseCase."""

    @pytest.mark.asyncio
    async def test_update_board_swimlanes_success(self, mock_board_repository, test_board):
        """Test successful update of board swimlane_type."""
        mock_board_repository.get_by_id.return_value = test_board
        test_board.update_swimlane_type("epic")
        mock_board_repository.update.return_value = test_board

        use_case = UpdateBoardSwimlanesUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, "epic")

        assert result.swimlane_type == "epic"
        mock_board_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_board_swimlanes_assignee(self, mock_board_repository, test_board):
        """Test update swimlane_type to assignee."""
        mock_board_repository.get_by_id.return_value = test_board
        test_board.update_swimlane_type("assignee")
        mock_board_repository.update.return_value = test_board

        use_case = UpdateBoardSwimlanesUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, "assignee")

        assert result.swimlane_type == "assignee"

    @pytest.mark.asyncio
    async def test_update_board_swimlanes_to_none(self, mock_board_repository, test_board):
        """Test update swimlane_type back to none."""
        test_board.update_swimlane_type("epic")
        mock_board_repository.get_by_id.return_value = test_board
        test_board.update_swimlane_type("none")
        mock_board_repository.update.return_value = test_board

        use_case = UpdateBoardSwimlanesUseCase(mock_board_repository)
        result = await use_case.execute(test_board.id, "none")

        assert result.swimlane_type == "none"

    @pytest.mark.asyncio
    async def test_update_board_swimlanes_board_not_found(self, mock_board_repository):
        """Test update swimlanes when board not found."""
        mock_board_repository.get_by_id.return_value = None

        use_case = UpdateBoardSwimlanesUseCase(mock_board_repository)
        with pytest.raises(EntityNotFoundException, match="Board"):
            await use_case.execute(uuid4(), "epic")

    @pytest.mark.asyncio
    async def test_update_board_swimlanes_invalid_type_raises(
        self, mock_board_repository, test_board
    ):
        """Test entity raises when swimlane_type is invalid."""
        mock_board_repository.get_by_id.return_value = test_board

        use_case = UpdateBoardSwimlanesUseCase(mock_board_repository)
        with pytest.raises(ValueError, match="swimlane_type"):
            await use_case.execute(test_board.id, "invalid")


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
            None,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 1
        assert result.lists[0].id == board_list.id
        assert result.lists[0].issues == []
        assert result.swimlane_type == "none"
        assert result.swimlanes == []

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
            None,
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
            None,
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
            None,
        )
        result = await use_case.execute(test_board.id)
        assert len(result.lists) == 1
        assert len(result.lists[0].issues) == 1
        issue_item = result.lists[0].issues[0]
        assert issue_item.title == "Task"
        assert issue_item.comment_count == 2
        assert issue_item.project_id == test_board.project_id
        assert issue_item.project_key == test_project.key

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
            None,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 2
        call_kw = mock_issue_repository.get_all.call_args_list[0].kwargs
        assert call_kw.get("assignee_id") == user_id
        call_kw2 = mock_issue_repository.get_all.call_args_list[1].kwargs
        assert call_kw2.get("sprint_id") == sprint_id

    @pytest.mark.asyncio
    async def test_get_board_issues_scope_filters_applied(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test scope filters: labels include/exclude, assignee, type, priority."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        issue_matching = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Matching",
            type="bug",
            priority="high",
            assignee_id=uuid4(),
        )
        issue_wrong_label = Issue.create(
            project_id=test_board.project_id,
            issue_number=2,
            title="Wrong label",
            type="bug",
            priority="high",
            assignee_id=issue_matching.assignee_id,
        )
        issue_excluded_label = Issue.create(
            project_id=test_board.project_id,
            issue_number=3,
            title="Excluded label",
            type="bug",
            priority="high",
            assignee_id=issue_matching.assignee_id,
        )
        issue_wrong_assignee = Issue.create(
            project_id=test_board.project_id,
            issue_number=4,
            title="Wrong assignee",
            type="bug",
            priority="high",
        )
        issue_wrong_type = Issue.create(
            project_id=test_board.project_id,
            issue_number=5,
            title="Wrong type",
            type="task",
            priority="high",
            assignee_id=issue_matching.assignee_id,
        )
        issue_wrong_priority = Issue.create(
            project_id=test_board.project_id,
            issue_number=6,
            title="Wrong priority",
            type="bug",
            priority="low",
            assignee_id=issue_matching.assignee_id,
        )

        include_label = uuid4()
        exclude_label = uuid4()

        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [
            issue_matching,
            issue_wrong_label,
            issue_excluded_label,
            issue_wrong_assignee,
            issue_wrong_type,
            issue_wrong_priority,
        ]

        # Labels for issues
        def _labels_for_issue(issue_id):
            from src.domain.entities import Label

            if issue_id == issue_matching.id:
                label = Label.create(project_id=test_project.id, name="L", color="#ffffff")
                label.id = include_label
                return [label]
            if issue_id == issue_wrong_label.id:
                return []
            if issue_id == issue_excluded_label.id:
                label = Label.create(project_id=test_project.id, name="X", color="#ffffff")
                label.id = exclude_label
                return [label]
            return []

        async def _labels_side_effect(issue_id):
            return _labels_for_issue(issue_id)

        mock_label_repository.get_labels_for_issue.side_effect = _labels_side_effect
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        test_board.scope_config = {
            "label_ids": [str(include_label)],
            "exclude_label_ids": [str(exclude_label)],
            "assignee_id": str(issue_matching.assignee_id),
            "types": ["bug"],
            "priorities": ["high"],
        }
        mock_board_repository.get_by_id.return_value = test_board

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 1
        issues = result.lists[0].issues
        assert len(issues) == 1
        assert issues[0].title == "Matching"

    @pytest.mark.asyncio
    async def test_get_board_issues_scope_fixed_user_alias(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test that fixed_user_id is treated as assignee scope when assignee_id not set."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        user_id = uuid4()
        issue = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Task",
            assignee_id=user_id,
        )
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [issue]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        test_board.scope_config = {"fixed_user_id": str(user_id)}
        mock_board_repository.get_by_id.return_value = test_board

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 1
        assert len(result.lists[0].issues) == 1
        # Ensure underlying repository was called with correct assignee_id from fixed_user_id
        call_kwargs = mock_issue_repository.get_all.call_args.kwargs
        assert call_kwargs.get("assignee_id") == user_id

    @pytest.mark.asyncio
    async def test_get_board_issues_scope_reporter_search_and_story_points(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test reporter_id, search_text and story_points range filters."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        reporter = uuid4()
        in_range = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Search match",
            description="Important bug to fix",
            reporter_id=reporter,
            story_points=5,
        )
        wrong_reporter = Issue.create(
            project_id=test_board.project_id,
            issue_number=2,
            title="Search match",
            description="Important bug to fix",
            reporter_id=uuid4(),
            story_points=5,
        )
        wrong_text = Issue.create(
            project_id=test_board.project_id,
            issue_number=3,
            title="Other task",
            description="Something else",
            reporter_id=reporter,
            story_points=5,
        )
        too_low = Issue.create(
            project_id=test_board.project_id,
            issue_number=4,
            title="Search match",
            description="Important bug to fix",
            reporter_id=reporter,
            story_points=2,
        )
        too_high = Issue.create(
            project_id=test_board.project_id,
            issue_number=5,
            title="Search match",
            description="Important bug to fix",
            reporter_id=reporter,
            story_points=13,
        )

        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [
            in_range,
            wrong_reporter,
            wrong_text,
            too_low,
            too_high,
        ]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        test_board.scope_config = {
            "reporter_id": str(reporter),
            "search_text": "important bug",
            "story_points_min": 3,
            "story_points_max": 8,
        }
        mock_board_repository.get_by_id.return_value = test_board

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert len(result.lists) == 1
        issues = result.lists[0].issues
        assert len(issues) == 1
        assert issues[0].title == "Search match"

    @pytest.mark.asyncio
    async def test_get_board_issues_swimlane_type_epic(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test board issues with swimlane_type epic groups by parent_issue_id."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        epic_id = uuid4()
        issue_with_epic = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Story",
            parent_issue_id=epic_id,
        )
        issue_no_epic = Issue.create(
            project_id=test_board.project_id,
            issue_number=2,
            title="Standalone",
            parent_issue_id=None,
        )
        test_board.swimlane_type = "epic"
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [
            issue_with_epic,
            issue_no_epic,
        ]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        epic_issue = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="My Epic",
            type="epic",
        )
        mock_issue_repository.get_by_id.side_effect = lambda i: epic_issue if i == epic_id else None

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert result.swimlane_type == "epic"
        assert result.lists == []
        assert len(result.swimlanes) == 2
        titles = {s.swimlane_title for s in result.swimlanes}
        assert "No epic" in titles
        assert "My Epic" in titles
        for s in result.swimlanes:
            assert len(s.lists) == 1
            if s.swimlane_title == "My Epic":
                assert len(s.lists[0].issues) == 1
                assert s.lists[0].issues[0].title == "Story"
            else:
                assert len(s.lists[0].issues) == 1
                assert s.lists[0].issues[0].title == "Standalone"

    @pytest.mark.asyncio
    async def test_get_board_issues_swimlane_type_assignee(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test board issues with swimlane_type assignee groups by assignee_id."""
        from src.domain.entities import Issue, User
        from src.domain.value_objects import Email, HashedPassword

        valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        user_id = uuid4()
        issue_assigned = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Assigned task",
            assignee_id=user_id,
        )
        issue_unassigned = Issue.create(
            project_id=test_board.project_id,
            issue_number=2,
            title="Unassigned",
            assignee_id=None,
        )
        test_board.swimlane_type = "assignee"
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [
            issue_assigned,
            issue_unassigned,
        ]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        mock_user_repository = AsyncMock()
        user = User(
            id=user_id,
            email=Email("dev@example.com"),
            password_hash=HashedPassword(valid_hash),
            name="Dev User",
        )
        mock_user_repository.get_by_id.return_value = user

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            mock_user_repository,
        )
        result = await use_case.execute(test_board.id)

        assert result.swimlane_type == "assignee"
        assert result.lists == []
        assert len(result.swimlanes) == 2
        for s in result.swimlanes:
            assert len(s.lists) == 1
            if s.swimlane_title == "Unassigned":
                assert len(s.lists[0].issues) == 1
                assert s.lists[0].issues[0].title == "Unassigned"
                assert s.assignee is None
            else:
                assert s.swimlane_title == "Dev User"
                assert s.assignee is not None
                assert s.assignee.id == user_id
                assert s.assignee.name == "Dev User"
                assert len(s.lists[0].issues) == 1
                assert s.lists[0].issues[0].title == "Assigned task"

    @pytest.mark.asyncio
    async def test_get_board_issues_swimlane_epic_not_found_fallback_title(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test epic swimlane when get_by_id returns None uses fallback title."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        epic_id = uuid4()
        issue_with_epic = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Story",
            parent_issue_id=epic_id,
        )
        test_board.swimlane_type = "epic"
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [issue_with_epic]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0
        mock_issue_repository.get_by_id.return_value = None

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert result.swimlane_type == "epic"
        assert len(result.swimlanes) == 1
        assert result.swimlanes[0].swimlane_title == f"Epic {epic_id}"

    @pytest.mark.asyncio
    async def test_get_board_issues_swimlane_assignee_no_user_repo(
        self,
        mock_board_repository,
        mock_issue_repository,
        mock_label_repository,
        mock_comment_repository,
        mock_project_repository_for_issues,
        test_board,
        test_project,
    ):
        """Test assignee swimlane with user_repository None uses id as title."""
        from src.domain.entities import Issue

        board_list = BoardList.create(
            board_id=test_board.id, list_type="label", list_config={}, position=0
        )
        user_id = uuid4()
        issue_assigned = Issue.create(
            project_id=test_board.project_id,
            issue_number=1,
            title="Task",
            assignee_id=user_id,
        )
        test_board.swimlane_type = "assignee"
        mock_board_repository.get_by_id.return_value = test_board
        mock_board_repository.get_lists_for_board.return_value = [board_list]
        mock_project_repository_for_issues.get_by_id.return_value = test_project
        mock_issue_repository.get_all.return_value = [issue_assigned]
        mock_label_repository.get_labels_for_issue.return_value = []
        mock_comment_repository.count_by_issue_id.return_value = 0
        mock_issue_repository.count.return_value = 0

        use_case = GetBoardIssuesUseCase(
            mock_board_repository,
            mock_issue_repository,
            mock_label_repository,
            mock_comment_repository,
            mock_project_repository_for_issues,
            None,
        )
        result = await use_case.execute(test_board.id)

        assert result.swimlane_type == "assignee"
        assert len(result.swimlanes) == 1
        assert result.swimlanes[0].swimlane_title == str(user_id)
        assert result.swimlanes[0].assignee is not None
        assert result.swimlanes[0].assignee.id == user_id
        assert result.swimlanes[0].assignee.name == str(user_id)


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


def test_extract_uuid_and_scope_str_list():
    """Test _extract_uuid and _extract_scope_str_list helpers."""
    from src.application.use_cases.board.get_board_issues import (
        _extract_scope_str_list,
        _extract_uuid,
    )

    u = uuid4()
    assert _extract_uuid(None) is None
    assert _extract_uuid(u) == u
    assert _extract_uuid(str(u)) == u
    assert _extract_uuid("not-a-uuid") is None

    allowed = {"task", "bug"}
    assert _extract_scope_str_list(None, allowed) == []
    assert _extract_scope_str_list("not-a-list", allowed) == []
    assert _extract_scope_str_list(["task", "bug", "foo", "task"], allowed) == ["task", "bug"]


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
        mock_board_repository.get_projects_for_board.return_value = [test_board.project_id]

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
