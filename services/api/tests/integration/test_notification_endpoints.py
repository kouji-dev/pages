"""Integration tests for notification endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import NotificationModel


@pytest.mark.asyncio
async def test_list_notifications_success(client: AsyncClient, test_user, db_session):
    """Test successful notification listing."""
    # Create notifications
    notification1 = NotificationModel(
        user_id=test_user.id,
        type="issue_assigned",
        title="Test Notification 1",
        content="Content 1",
        entity_type="issue",
        entity_id=uuid4(),
        read=False,
    )
    notification2 = NotificationModel(
        user_id=test_user.id,
        type="issue_commented",
        title="Test Notification 2",
        content="Content 2",
        entity_type="issue",
        entity_id=uuid4(),
        read=True,
    )
    db_session.add_all([notification1, notification2])
    await db_session.flush()

    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List all notifications
    response = await client.get(
        "/api/v1/notifications",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 50
    assert len(data["notifications"]) == 2


@pytest.mark.asyncio
async def test_list_notifications_filtered_by_read(client: AsyncClient, test_user, db_session):
    """Test notification listing filtered by read status."""
    # Create notifications
    unread_notification = NotificationModel(
        user_id=test_user.id,
        type="issue_assigned",
        title="Unread Notification",
        content="Unread",
        read=False,
    )
    read_notification = NotificationModel(
        user_id=test_user.id,
        type="issue_commented",
        title="Read Notification",
        content="Read",
        read=True,
    )
    db_session.add_all([unread_notification, read_notification])
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List unread notifications only
    response = await client.get(
        "/api/v1/notifications?read=false",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["notifications"][0]["read"] is False


@pytest.mark.asyncio
async def test_list_notifications_with_pagination(client: AsyncClient, test_user, db_session):
    """Test notification listing with pagination."""
    # Create 15 notifications
    notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_assigned",
            title=f"Notification {i}",
            content=f"Content {i}",
            read=False,
        )
        for i in range(15)
    ]
    db_session.add_all(notifications)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get page 2 with limit 5
    response = await client.get(
        "/api/v1/notifications?page=2&limit=5",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["page"] == 2
    assert data["limit"] == 5
    assert data["pages"] == 3
    assert len(data["notifications"]) == 5


@pytest.mark.asyncio
async def test_mark_notification_as_read_success(client: AsyncClient, test_user, db_session):
    """Test successful notification mark as read."""
    # Create notification
    notification = NotificationModel(
        user_id=test_user.id,
        type="issue_assigned",
        title="Test Notification",
        content="Content",
        read=False,
    )
    db_session.add(notification)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Mark as read
    response = await client.put(
        f"/api/v1/notifications/{notification.id}/read",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(notification.id)
    assert data["read"] is True

    # Verify in database
    await db_session.refresh(notification)
    assert notification.read is True


@pytest.mark.asyncio
async def test_mark_notification_as_read_not_found(client: AsyncClient, test_user, db_session):
    """Test mark as read with non-existent notification."""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Try to mark non-existent notification as read
    fake_id = uuid4()
    response = await client.put(
        f"/api/v1/notifications/{fake_id}/read",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mark_all_notifications_as_read_success(client: AsyncClient, test_user, db_session):
    """Test successful mark all notifications as read."""
    # Create unread notifications
    notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_assigned",
            title=f"Notification {i}",
            content=f"Content {i}",
            read=False,
        )
        for i in range(5)
    ]
    db_session.add_all(notifications)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Mark all as read
    response = await client.put(
        "/api/v1/notifications/read-all",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["marked_count"] == 5

    # Verify in database
    for notif in notifications:
        await db_session.refresh(notif)
        assert notif.read is True


@pytest.mark.asyncio
async def test_mark_all_notifications_as_read_no_unread(client: AsyncClient, test_user, db_session):
    """Test mark all as read when no unread notifications."""
    # Create already read notifications
    notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_assigned",
            title=f"Notification {i}",
            content=f"Content {i}",
            read=True,
        )
        for i in range(3)
    ]
    db_session.add_all(notifications)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Mark all as read
    response = await client.put(
        "/api/v1/notifications/read-all",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["marked_count"] == 0


@pytest.mark.asyncio
async def test_get_unread_count_success(client: AsyncClient, test_user, db_session):
    """Test successful unread notification count retrieval."""
    # Create notifications (3 unread, 2 read)
    unread_notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_assigned",
            title=f"Unread Notification {i}",
            content=f"Content {i}",
            read=False,
        )
        for i in range(3)
    ]
    read_notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_commented",
            title=f"Read Notification {i}",
            content=f"Content {i}",
            read=True,
        )
        for i in range(2)
    ]
    db_session.add_all(unread_notifications + read_notifications)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get unread count
    response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 3


@pytest.mark.asyncio
async def test_get_unread_count_zero(client: AsyncClient, test_user, db_session):
    """Test unread count when no unread notifications."""
    # Create only read notifications
    read_notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_commented",
            title=f"Read Notification {i}",
            content=f"Content {i}",
            read=True,
        )
        for i in range(2)
    ]
    db_session.add_all(read_notifications)
    await db_session.flush()

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get unread count
    response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0


@pytest.mark.asyncio
async def test_list_notifications_unauthorized(client: AsyncClient):
    """Test notification listing without authentication."""
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_notifications_other_user_isolation(client: AsyncClient, test_user, db_session):
    """Test that users only see their own notifications."""
    # Create a second user
    from src.infrastructure.database.models import UserModel

    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    test_user2 = UserModel(
        email="testuser2@example.com",
        password_hash=valid_hash,
        name="Test User 2",
        is_active=True,
    )
    db_session.add(test_user2)
    await db_session.flush()

    # Create notifications for user 1
    user1_notifications = [
        NotificationModel(
            user_id=test_user.id,
            type="issue_assigned",
            title="User 1 Notification",
            content="Content",
            read=False,
        )
    ]

    # Create notifications for user 2
    user2_notifications = [
        NotificationModel(
            user_id=test_user2.id,
            type="issue_assigned",
            title="User 2 Notification",
            content="Content",
            read=False,
        )
    ]

    db_session.add_all(user1_notifications + user2_notifications)
    await db_session.flush()

    # Login as user 1
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email.value,
            "password": "TestPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # List notifications
    response = await client.get(
        "/api/v1/notifications",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    # User 1 should only see their own notification
    assert data["total"] == 1
    assert data["notifications"][0]["title"] == "User 1 Notification"
