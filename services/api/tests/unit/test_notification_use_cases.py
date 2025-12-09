"""Unit tests for notification use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.notification import (
    GetUnreadCountUseCase,
    ListNotificationsUseCase,
    MarkAllAsReadUseCase,
    MarkAsReadUseCase,
)
from src.domain.entities import Notification
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects.notification_type import NotificationType


@pytest.fixture
def mock_notification_repository():
    """Mock notification repository."""
    return AsyncMock()


@pytest.fixture
def test_user_id():
    """Create a test user ID."""
    return uuid4()


@pytest.fixture
def test_notification(test_user_id):
    """Create a test notification."""
    return Notification.create(
        user_id=test_user_id,
        type=NotificationType.ISSUE_ASSIGNED,
        title="Test Notification",
        content="This is a test notification",
        entity_type="issue",
        entity_id=uuid4(),
    )


class TestListNotificationsUseCase:
    """Tests for ListNotificationsUseCase."""

    @pytest.mark.asyncio
    async def test_list_notifications_success(
        self, mock_notification_repository, test_user_id, test_notification
    ):
        """Test successful notification listing."""
        # Setup mocks
        mock_notification_repository.get_by_user_id.return_value = [test_notification]
        mock_notification_repository.count_by_user_id.return_value = 1

        # Execute use case
        use_case = ListNotificationsUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id))

        # Verify
        assert result.total == 1
        assert result.page == 1
        assert result.limit == 50
        assert result.pages == 1
        assert len(result.notifications) == 1
        assert result.notifications[0].id == test_notification.id
        mock_notification_repository.get_by_user_id.assert_called_once()
        mock_notification_repository.count_by_user_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_notifications_with_filters(
        self, mock_notification_repository, test_user_id
    ):
        """Test listing notifications with read filter."""
        # Setup mocks
        mock_notification_repository.get_by_user_id.return_value = []
        mock_notification_repository.count_by_user_id.return_value = 0

        # Execute use case with read filter
        use_case = ListNotificationsUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id), read=False)

        # Verify
        assert result.total == 0
        assert len(result.notifications) == 0
        mock_notification_repository.get_by_user_id.assert_called_once_with(
            test_user_id, skip=0, limit=50, read=False
        )

    @pytest.mark.asyncio
    async def test_list_notifications_with_pagination(
        self, mock_notification_repository, test_user_id, test_notification
    ):
        """Test listing notifications with pagination."""
        # Setup mocks
        notifications = [test_notification for _ in range(5)]
        mock_notification_repository.get_by_user_id.return_value = notifications
        mock_notification_repository.count_by_user_id.return_value = 15

        # Execute use case with pagination
        use_case = ListNotificationsUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id), page=2, limit=5)

        # Verify
        assert result.total == 15
        assert result.page == 2
        assert result.limit == 5
        assert result.pages == 3
        assert len(result.notifications) == 5
        mock_notification_repository.get_by_user_id.assert_called_once_with(
            test_user_id, skip=5, limit=5, read=None
        )


class TestMarkAsReadUseCase:
    """Tests for MarkAsReadUseCase."""

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, mock_notification_repository, test_notification):
        """Test successful notification mark as read."""
        # Setup mocks
        test_notification.mark_as_read()
        mock_notification_repository.mark_as_read.return_value = test_notification

        # Execute use case
        use_case = MarkAsReadUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_notification.id))

        # Verify
        assert result.id == test_notification.id
        assert result.read is True
        mock_notification_repository.mark_as_read.assert_called_once_with(test_notification.id)

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, mock_notification_repository):
        """Test mark as read with non-existent notification."""
        fake_id = uuid4()

        # Setup mocks
        mock_notification_repository.mark_as_read.side_effect = EntityNotFoundException(
            "Notification", str(fake_id)
        )

        # Execute use case
        use_case = MarkAsReadUseCase(mock_notification_repository)

        # Verify exception is raised
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(fake_id))


class TestMarkAllAsReadUseCase:
    """Tests for MarkAllAsReadUseCase."""

    @pytest.mark.asyncio
    async def test_mark_all_as_read_success(self, mock_notification_repository, test_user_id):
        """Test successful mark all as read."""
        # Setup mocks
        mock_notification_repository.mark_all_as_read.return_value = 5

        # Execute use case
        use_case = MarkAllAsReadUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id))

        # Verify
        assert result.marked_count == 5
        mock_notification_repository.mark_all_as_read.assert_called_once_with(test_user_id)

    @pytest.mark.asyncio
    async def test_mark_all_as_read_no_unread(self, mock_notification_repository, test_user_id):
        """Test mark all as read when no unread notifications."""
        # Setup mocks
        mock_notification_repository.mark_all_as_read.return_value = 0

        # Execute use case
        use_case = MarkAllAsReadUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id))

        # Verify
        assert result.marked_count == 0
        mock_notification_repository.mark_all_as_read.assert_called_once_with(test_user_id)


class TestGetUnreadCountUseCase:
    """Tests for GetUnreadCountUseCase."""

    @pytest.mark.asyncio
    async def test_get_unread_count_success(self, mock_notification_repository, test_user_id):
        """Test successful unread count retrieval."""
        # Setup mocks
        mock_notification_repository.count_unread.return_value = 10

        # Execute use case
        use_case = GetUnreadCountUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id))

        # Verify
        assert result.unread_count == 10
        mock_notification_repository.count_unread.assert_called_once_with(test_user_id)

    @pytest.mark.asyncio
    async def test_get_unread_count_zero(self, mock_notification_repository, test_user_id):
        """Test unread count when no unread notifications."""
        # Setup mocks
        mock_notification_repository.count_unread.return_value = 0

        # Execute use case
        use_case = GetUnreadCountUseCase(mock_notification_repository)
        result = await use_case.execute(str(test_user_id))

        # Verify
        assert result.unread_count == 0
        mock_notification_repository.count_unread.assert_called_once_with(test_user_id)
