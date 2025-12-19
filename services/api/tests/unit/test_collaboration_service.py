"""Unit tests for collaboration service."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.services.collaboration_service import CollaborationService
from src.domain.entities import Page, Presence, Space, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_presence_repository():
    """Mock presence repository."""
    return AsyncMock()


@pytest.fixture
def mock_page_repository():
    """Mock page repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
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
def test_page(test_space, test_user):
    """Create a test page."""
    return Page.create(
        space_id=test_space.id,
        title="Test Page",
        content="Test content",
        created_by=test_user.id,
    )


@pytest.fixture
def test_presence(test_page, test_user):
    """Create a test presence."""
    return Presence.create(
        page_id=test_page.id,
        user_id=test_user.id,
        socket_id="socket123",
    )


class TestCollaborationService:
    """Tests for CollaborationService."""

    @pytest.mark.asyncio
    async def test_join_page_success(
        self,
        mock_presence_repository,
        mock_page_repository,
        mock_user_repository,
        test_page,
        test_user,
        test_presence,
    ):
        """Test successful page join."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_user_repository.get_by_id.return_value = test_user
        mock_presence_repository.get_by_page_and_user.return_value = None
        mock_presence_repository.create.return_value = test_presence

        service = CollaborationService(
            mock_presence_repository, mock_page_repository, mock_user_repository
        )
        result = await service.join_page(
            page_id=test_page.id,
            user_id=test_user.id,
            socket_id="socket123",
        )

        assert result.socket_id == "socket123"
        mock_page_repository.get_by_id.assert_called_once()
        mock_user_repository.get_by_id.assert_called_once()
        mock_presence_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_join_page_page_not_found(
        self, mock_presence_repository, mock_page_repository, mock_user_repository
    ):
        """Test page join when page not found."""
        mock_page_repository.get_by_id.return_value = None

        service = CollaborationService(
            mock_presence_repository, mock_page_repository, mock_user_repository
        )

        with pytest.raises(EntityNotFoundException):
            await service.join_page(
                page_id=uuid4(),
                user_id=uuid4(),
                socket_id="socket123",
            )

    @pytest.mark.asyncio
    async def test_update_cursor_success(
        self,
        mock_presence_repository,
        mock_page_repository,
        mock_user_repository,
        test_presence,
    ):
        """Test successful cursor update."""
        mock_presence_repository.get_by_page_and_user.return_value = test_presence
        mock_presence_repository.update.return_value = test_presence

        service = CollaborationService(
            mock_presence_repository, mock_page_repository, mock_user_repository
        )
        result = await service.update_cursor(
            page_id=test_presence.page_id,
            user_id=test_presence.user_id,
            cursor_position='{"line": 1, "column": 5}',
        )

        assert result.cursor_position == '{"line": 1, "column": 5}'

    @pytest.mark.asyncio
    async def test_get_page_presences_success(
        self,
        mock_presence_repository,
        mock_page_repository,
        mock_user_repository,
        test_presence,
    ):
        """Test successful getting page presences."""
        mock_presence_repository.get_all_by_page.return_value = [test_presence]

        service = CollaborationService(
            mock_presence_repository, mock_page_repository, mock_user_repository
        )
        result = await service.get_page_presences(test_presence.page_id)

        assert len(result) == 1
        assert result[0].user_id == test_presence.user_id

    @pytest.mark.asyncio
    async def test_disconnect_socket_success(
        self,
        mock_presence_repository,
        mock_page_repository,
        mock_user_repository,
    ):
        """Test successful socket disconnection."""
        service = CollaborationService(
            mock_presence_repository, mock_page_repository, mock_user_repository
        )
        await service.disconnect_socket("socket123")

        mock_presence_repository.delete_by_socket_id.assert_called_once_with("socket123")
