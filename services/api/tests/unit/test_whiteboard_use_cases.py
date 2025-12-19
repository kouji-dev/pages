"""Unit tests for whiteboard use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.whiteboard import CreateWhiteboardRequest, UpdateWhiteboardRequest
from src.application.use_cases.whiteboard import (
    CreateWhiteboardUseCase,
    DeleteWhiteboardUseCase,
    GetWhiteboardUseCase,
    ListWhiteboardsUseCase,
    UpdateWhiteboardUseCase,
)
from src.domain.entities import Space, User, Whiteboard
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_whiteboard_repository():
    """Mock whiteboard repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create a test user."""
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
        is_active=True,
    )


@pytest.fixture
def test_space(test_user):
    """Create a test space."""
    return Space.create(
        organization_id=uuid4(),
        name="Test Space",
        key="TEST",
    )


@pytest.fixture
def test_whiteboard(test_space, test_user):
    """Create a test whiteboard."""
    return Whiteboard.create(
        space_id=test_space.id,
        name="Test Whiteboard",
        data='{"elements": []}',
        created_by=test_user.id,
    )


class TestCreateWhiteboardUseCase:
    """Tests for CreateWhiteboardUseCase."""

    @pytest.mark.asyncio
    async def test_create_whiteboard_success(
        self,
        mock_whiteboard_repository,
        mock_space_repository,
        test_space,
        test_whiteboard,
        test_user,
    ):
        """Test successful whiteboard creation."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_whiteboard_repository.create.return_value = test_whiteboard

        request = CreateWhiteboardRequest(
            space_id=test_space.id,
            name="Test Whiteboard",
        )

        use_case = CreateWhiteboardUseCase(mock_whiteboard_repository, mock_space_repository)
        result = await use_case.execute(request, str(test_user.id))

        assert result.name == "Test Whiteboard"
        mock_space_repository.get_by_id.assert_called_once()
        mock_whiteboard_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_whiteboard_space_not_found(
        self, mock_whiteboard_repository, mock_space_repository
    ):
        """Test whiteboard creation when space not found."""
        mock_space_repository.get_by_id.return_value = None

        request = CreateWhiteboardRequest(space_id=uuid4(), name="Test Whiteboard")

        use_case = CreateWhiteboardUseCase(mock_whiteboard_repository, mock_space_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request, str(uuid4()))


class TestListWhiteboardsUseCase:
    """Tests for ListWhiteboardsUseCase."""

    @pytest.mark.asyncio
    async def test_list_whiteboards_success(
        self, mock_whiteboard_repository, mock_space_repository, test_space, test_whiteboard
    ):
        """Test successful whiteboard listing."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_whiteboard_repository.get_all.return_value = [test_whiteboard]
        mock_whiteboard_repository.count.return_value = 1

        use_case = ListWhiteboardsUseCase(mock_whiteboard_repository, mock_space_repository)
        result = await use_case.execute(str(test_space.id), page=1, limit=20)

        assert result.total == 1
        assert len(result.whiteboards) == 1
        assert result.whiteboards[0].name == "Test Whiteboard"

    @pytest.mark.asyncio
    async def test_list_whiteboards_space_not_found(
        self, mock_whiteboard_repository, mock_space_repository
    ):
        """Test whiteboard listing when space not found."""
        mock_space_repository.get_by_id.return_value = None

        use_case = ListWhiteboardsUseCase(mock_whiteboard_repository, mock_space_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestGetWhiteboardUseCase:
    """Tests for GetWhiteboardUseCase."""

    @pytest.mark.asyncio
    async def test_get_whiteboard_success(self, mock_whiteboard_repository, test_whiteboard):
        """Test successful whiteboard retrieval."""
        mock_whiteboard_repository.get_by_id.return_value = test_whiteboard

        use_case = GetWhiteboardUseCase(mock_whiteboard_repository)
        result = await use_case.execute(str(test_whiteboard.id))

        assert result.name == "Test Whiteboard"

    @pytest.mark.asyncio
    async def test_get_whiteboard_not_found(self, mock_whiteboard_repository):
        """Test whiteboard retrieval when whiteboard not found."""
        mock_whiteboard_repository.get_by_id.return_value = None

        use_case = GetWhiteboardUseCase(mock_whiteboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdateWhiteboardUseCase:
    """Tests for UpdateWhiteboardUseCase."""

    @pytest.mark.asyncio
    async def test_update_whiteboard_success(
        self, mock_whiteboard_repository, test_whiteboard, test_user
    ):
        """Test successful whiteboard update."""
        mock_whiteboard_repository.get_by_id.return_value = test_whiteboard
        mock_whiteboard_repository.update.return_value = test_whiteboard

        request = UpdateWhiteboardRequest(name="Updated Whiteboard")

        use_case = UpdateWhiteboardUseCase(mock_whiteboard_repository)
        result = await use_case.execute(str(test_whiteboard.id), request, str(test_user.id))

        assert result.name == "Updated Whiteboard"

    @pytest.mark.asyncio
    async def test_update_whiteboard_not_found(self, mock_whiteboard_repository):
        """Test whiteboard update when whiteboard not found."""
        mock_whiteboard_repository.get_by_id.return_value = None

        request = UpdateWhiteboardRequest(name="Updated Whiteboard")

        use_case = UpdateWhiteboardUseCase(mock_whiteboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request, str(uuid4()))


class TestDeleteWhiteboardUseCase:
    """Tests for DeleteWhiteboardUseCase."""

    @pytest.mark.asyncio
    async def test_delete_whiteboard_success(self, mock_whiteboard_repository, test_whiteboard):
        """Test successful whiteboard deletion."""
        mock_whiteboard_repository.get_by_id.return_value = test_whiteboard

        use_case = DeleteWhiteboardUseCase(mock_whiteboard_repository)
        await use_case.execute(str(test_whiteboard.id))

        mock_whiteboard_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_whiteboard_not_found(self, mock_whiteboard_repository):
        """Test whiteboard deletion when whiteboard not found."""
        mock_whiteboard_repository.get_by_id.return_value = None

        use_case = DeleteWhiteboardUseCase(mock_whiteboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
