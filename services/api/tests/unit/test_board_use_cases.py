"""Unit tests for board use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.board import CreateBoardRequest, UpdateBoardRequest
from src.application.use_cases.board import (
    CreateBoardUseCase,
    DeleteBoardUseCase,
    GetBoardUseCase,
    ListProjectBoardsUseCase,
    UpdateBoardUseCase,
)
from src.domain.entities import Board, Project
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
