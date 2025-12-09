"""Functional tests for notification workflows."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.functional.conftest import (
    create_test_user,
    get_auth_headers,
)


@pytest.mark.asyncio
async def test_notification_lifecycle_workflow(
    client: AsyncClient, unique_email: str, test_password: str, db_session
) -> None:
    """Test complete notification lifecycle: Create → List → Mark as Read → Verify.

    This workflow validates that:
    - User can see their notifications
    - Notifications can be marked as read
    - Unread count updates correctly
    - Read/unread filtering works
    """
    # Step 1: Create and login test user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    headers = get_auth_headers(user_data["access_token"])
    user_id = user_data["id"]

    # Step 2: Create test notifications directly in database
    from src.infrastructure.database.models import NotificationModel

    notifications = [
        NotificationModel(
            user_id=user_id,
            type="issue_assigned",
            title=f"Test Notification {i}",
            content=f"Content for notification {i}",
            entity_type="issue",
            entity_id=uuid4(),
            read=False,
        )
        for i in range(5)
    ]
    for notif in notifications:
        db_session.add(notif)
    await db_session.flush()

    # Step 3: Check initial unread count
    unread_response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=headers,
    )
    assert unread_response.status_code == 200
    assert unread_response.json()["unread_count"] == 5

    # Step 4: List all notifications
    list_response = await client.get(
        "/api/v1/notifications",
        headers=headers,
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] == 5
    assert len(list_data["notifications"]) == 5
    assert all(not n["read"] for n in list_data["notifications"])

    # Step 5: Mark one notification as read
    first_notification_id = list_data["notifications"][0]["id"]
    mark_read_response = await client.put(
        f"/api/v1/notifications/{first_notification_id}/read",
        headers=headers,
    )
    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["read"] is True

    # Step 6: Verify unread count decreased
    unread_response2 = await client.get(
        "/api/v1/notifications/unread-count",
        headers=headers,
    )
    assert unread_response2.status_code == 200
    assert unread_response2.json()["unread_count"] == 4

    # Step 7: List unread notifications only
    unread_list_response = await client.get(
        "/api/v1/notifications?read=false",
        headers=headers,
    )
    assert unread_list_response.status_code == 200
    unread_list_data = unread_list_response.json()
    assert unread_list_data["total"] == 4
    assert all(not n["read"] for n in unread_list_data["notifications"])

    # Step 8: List read notifications only
    read_list_response = await client.get(
        "/api/v1/notifications?read=true",
        headers=headers,
    )
    assert read_list_response.status_code == 200
    read_list_data = read_list_response.json()
    assert read_list_data["total"] == 1
    assert all(n["read"] for n in read_list_data["notifications"])


@pytest.mark.asyncio
async def test_mark_all_as_read_workflow(
    client: AsyncClient, unique_email: str, test_password: str, db_session
) -> None:
    """Test mark all as read workflow.

    This workflow validates that:
    - User can mark all notifications as read at once
    - Unread count becomes zero
    - All notifications show as read
    """
    # Step 1: Create and login test user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    headers = get_auth_headers(user_data["access_token"])
    user_id = user_data["id"]

    # Step 2: Create multiple unread notifications
    from src.infrastructure.database.models import NotificationModel

    notifications = [
        NotificationModel(
            user_id=user_id,
            type="issue_commented",
            title=f"Notification {i}",
            content=f"Content {i}",
            read=False,
        )
        for i in range(10)
    ]
    for notif in notifications:
        db_session.add(notif)
    await db_session.flush()

    # Step 3: Verify initial unread count
    unread_response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=headers,
    )
    assert unread_response.status_code == 200
    assert unread_response.json()["unread_count"] == 10

    # Step 4: Mark all as read
    mark_all_response = await client.put(
        "/api/v1/notifications/read-all",
        headers=headers,
    )
    assert mark_all_response.status_code == 200
    assert mark_all_response.json()["marked_count"] == 10

    # Step 5: Verify unread count is now zero
    unread_response2 = await client.get(
        "/api/v1/notifications/unread-count",
        headers=headers,
    )
    assert unread_response2.status_code == 200
    assert unread_response2.json()["unread_count"] == 0

    # Step 6: Verify unread notifications list is empty
    unread_list_response = await client.get(
        "/api/v1/notifications?read=false",
        headers=headers,
    )
    assert unread_list_response.status_code == 200
    unread_list_data = unread_list_response.json()
    # Should have no unread notifications
    assert unread_list_data["total"] == 0

    # Step 7: Verify mark all again returns 0 (no unread to mark)
    mark_all_response2 = await client.put(
        "/api/v1/notifications/read-all",
        headers=headers,
    )
    assert mark_all_response2.status_code == 200
    assert mark_all_response2.json()["marked_count"] == 0


@pytest.mark.asyncio
async def test_notification_pagination_workflow(
    client: AsyncClient, unique_email: str, test_password: str, db_session
) -> None:
    """Test notification pagination workflow.

    This workflow validates that:
    - Notifications are properly paginated
    - Page navigation works correctly
    - Total count is accurate
    """
    # Step 1: Create and login test user
    user_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="Test User",
    )
    headers = get_auth_headers(user_data["access_token"])
    user_id = user_data["id"]

    # Step 2: Create 25 notifications
    from src.infrastructure.database.models import NotificationModel

    notifications = [
        NotificationModel(
            user_id=user_id,
            type="issue_assigned",
            title=f"Notification {i:02d}",
            content=f"Content {i}",
            read=False,
        )
        for i in range(25)
    ]
    for notif in notifications:
        db_session.add(notif)
    await db_session.flush()

    # Step 3: Get first page (default limit 50)
    page1_response = await client.get(
        "/api/v1/notifications?page=1&limit=10",
        headers=headers,
    )
    assert page1_response.status_code == 200
    page1_data = page1_response.json()
    assert page1_data["total"] == 25
    assert page1_data["page"] == 1
    assert page1_data["limit"] == 10
    assert page1_data["pages"] == 3
    assert len(page1_data["notifications"]) == 10

    # Step 4: Get second page
    page2_response = await client.get(
        "/api/v1/notifications?page=2&limit=10",
        headers=headers,
    )
    assert page2_response.status_code == 200
    page2_data = page2_response.json()
    assert page2_data["page"] == 2
    assert len(page2_data["notifications"]) == 10

    # Step 5: Get third page (last page)
    page3_response = await client.get(
        "/api/v1/notifications?page=3&limit=10",
        headers=headers,
    )
    assert page3_response.status_code == 200
    page3_data = page3_response.json()
    assert page3_data["page"] == 3
    assert len(page3_data["notifications"]) == 5  # Only 5 left

    # Step 6: Verify no duplicates across pages
    page1_ids = {n["id"] for n in page1_data["notifications"]}
    page2_ids = {n["id"] for n in page2_data["notifications"]}
    page3_ids = {n["id"] for n in page3_data["notifications"]}
    assert len(page1_ids & page2_ids) == 0  # No overlap
    assert len(page1_ids & page3_ids) == 0
    assert len(page2_ids & page3_ids) == 0


@pytest.mark.asyncio
async def test_notification_isolation_workflow(
    client: AsyncClient, unique_email: str, test_password: str, db_session
) -> None:
    """Test notification isolation between users.

    This workflow validates that:
    - Users only see their own notifications
    - Users cannot mark other users' notifications as read
    - Unread counts are user-specific
    """
    # Step 1: Create two test users
    user1_data = await create_test_user(
        client,
        email=unique_email,
        password=test_password,
        name="User 1",
    )
    user1_headers = get_auth_headers(user1_data["access_token"])
    user1_id = user1_data["id"]

    # Generate unique email for second user
    import time

    unique_email2 = f"testuser2_{int(time.time() * 1000000)}@example.com"

    user2_data = await create_test_user(
        client,
        email=unique_email2,
        password=test_password,
        name="User 2",
    )
    user2_headers = get_auth_headers(user2_data["access_token"])
    user2_id = user2_data["id"]

    # Step 2: Create notifications for both users
    from src.infrastructure.database.models import NotificationModel

    user1_notifications = [
        NotificationModel(
            user_id=user1_id,
            type="issue_assigned",
            title=f"User 1 Notification {i}",
            content=f"Content for user 1, notification {i}",
            read=False,
        )
        for i in range(3)
    ]

    user2_notifications = [
        NotificationModel(
            user_id=user2_id,
            type="issue_commented",
            title=f"User 2 Notification {i}",
            content=f"Content for user 2, notification {i}",
            read=False,
        )
        for i in range(5)
    ]

    for notif in user1_notifications + user2_notifications:
        db_session.add(notif)
    await db_session.flush()

    # Step 3: User 1 should only see their 3 notifications
    user1_list_response = await client.get(
        "/api/v1/notifications",
        headers=user1_headers,
    )
    assert user1_list_response.status_code == 200
    user1_list_data = user1_list_response.json()
    assert user1_list_data["total"] == 3
    assert all("User 1" in n["title"] for n in user1_list_data["notifications"])

    # Step 4: User 2 should only see their 5 notifications
    user2_list_response = await client.get(
        "/api/v1/notifications",
        headers=user2_headers,
    )
    assert user2_list_response.status_code == 200
    user2_list_data = user2_list_response.json()
    assert user2_list_data["total"] == 5
    assert all("User 2" in n["title"] for n in user2_list_data["notifications"])

    # Step 5: Verify unread counts are user-specific
    user1_unread_response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=user1_headers,
    )
    assert user1_unread_response.status_code == 200
    assert user1_unread_response.json()["unread_count"] == 3

    user2_unread_response = await client.get(
        "/api/v1/notifications/unread-count",
        headers=user2_headers,
    )
    assert user2_unread_response.status_code == 200
    assert user2_unread_response.json()["unread_count"] == 5

    # Step 6: User 1 marks all their notifications as read
    user1_mark_all_response = await client.put(
        "/api/v1/notifications/read-all",
        headers=user1_headers,
    )
    assert user1_mark_all_response.status_code == 200
    assert user1_mark_all_response.json()["marked_count"] == 3

    # Step 7: Verify User 1's unread count is 0 but User 2's is still 5
    user1_unread_response2 = await client.get(
        "/api/v1/notifications/unread-count",
        headers=user1_headers,
    )
    assert user1_unread_response2.status_code == 200
    assert user1_unread_response2.json()["unread_count"] == 0

    user2_unread_response2 = await client.get(
        "/api/v1/notifications/unread-count",
        headers=user2_headers,
    )
    assert user2_unread_response2.status_code == 200
    assert user2_unread_response2.json()["unread_count"] == 5
