"""Integration tests for attachment endpoints."""

import io

import pytest
from httpx import AsyncClient

from src.infrastructure.database.models import (
    AttachmentModel,
    IssueModel,
    OrganizationMemberModel,
    OrganizationModel,
    ProjectModel,
)


@pytest.mark.asyncio
async def test_upload_attachment_success(client: AsyncClient, test_user, db_session):
    """Test successful attachment upload."""
    # Create organization
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    # Add user as member
    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    # Create project
    project = ProjectModel(
        organization_id=org.id,
        name="Test Project",
        key="TEST",
    )
    db_session.add(project)
    await db_session.flush()

    # Create issue
    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        description="A test issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
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

    # Upload attachment
    file_content = b"test file content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

    upload_response = await client.post(
        f"/api/v1/issues/{issue.id}/attachments",
        files=files,
        headers=auth_headers,
    )

    assert upload_response.status_code == 201
    data = upload_response.json()
    assert data["original_name"] == "test.pdf"
    assert data["file_size"] == len(file_content)
    assert data["mime_type"] == "application/pdf"
    assert data["entity_id"] == str(issue.id)
    assert data["entity_type"] == "issue"
    assert data["uploaded_by"] == str(test_user.id)
    assert "id" in data
    assert "storage_path" in data
    assert "download_url" in data


@pytest.mark.asyncio
async def test_get_attachment_success(client: AsyncClient, test_user, db_session):
    """Test successful attachment retrieval."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
    await db_session.flush()

    attachment = AttachmentModel(
        entity_type="issue",
        entity_id=issue.id,
        file_name="test_file.pdf",
        original_name="test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        storage_path="attachments/test/test_file.pdf",
        uploaded_by=test_user.id,
    )
    db_session.add(attachment)
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

    # Get attachment
    get_response = await client.get(
        f"/api/v1/attachments/{attachment.id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == str(attachment.id)
    assert data["original_name"] == "test.pdf"
    assert data["file_size"] == 1024


@pytest.mark.asyncio
async def test_list_attachments_success(client: AsyncClient, test_user, db_session):
    """Test successful attachment listing."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
    await db_session.flush()

    # Create attachments
    attachment1 = AttachmentModel(
        entity_type="issue",
        entity_id=issue.id,
        file_name="file1.pdf",
        original_name="test1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        storage_path="attachments/test/file1.pdf",
        uploaded_by=test_user.id,
    )
    attachment2 = AttachmentModel(
        entity_type="issue",
        entity_id=issue.id,
        file_name="file2.pdf",
        original_name="test2.pdf",
        file_size=2048,
        mime_type="application/pdf",
        storage_path="attachments/test/file2.pdf",
        uploaded_by=test_user.id,
    )
    db_session.add(attachment1)
    db_session.add(attachment2)
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

    # List attachments
    list_response = await client.get(
        f"/api/v1/issues/{issue.id}/attachments",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 2
    assert len(data["attachments"]) == 2
    # Attachments should be ordered by created_at ASC
    assert data["attachments"][0]["original_name"] == "test1.pdf"
    assert data["attachments"][1]["original_name"] == "test2.pdf"


@pytest.mark.asyncio
async def test_delete_attachment_success(client: AsyncClient, test_user, db_session):
    """Test successful attachment deletion."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
    await db_session.flush()

    attachment = AttachmentModel(
        entity_type="issue",
        entity_id=issue.id,
        file_name="test_file.pdf",
        original_name="test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        storage_path="attachments/test/test_file.pdf",
        uploaded_by=test_user.id,
    )
    db_session.add(attachment)
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

    # Delete attachment
    delete_response = await client.delete(
        f"/api/v1/attachments/{attachment.id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Verify attachment is deleted from database
    from sqlalchemy import select

    result = await db_session.execute(
        select(AttachmentModel).where(AttachmentModel.id == attachment.id)
    )
    deleted_attachment = result.scalar_one_or_none()
    assert deleted_attachment is None


@pytest.mark.asyncio
async def test_upload_attachment_invalid_file_type(client: AsyncClient, test_user, db_session):
    """Test attachment upload with invalid file type."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
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

    # Try to upload executable file
    file_content = b"executable content"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}

    upload_response = await client.post(
        f"/api/v1/issues/{issue.id}/attachments",
        files=files,
        headers=auth_headers,
    )

    assert upload_response.status_code == 400
    error_data = upload_response.json()
    assert "not allowed" in error_data.get("message", error_data.get("detail", "")).lower()


@pytest.mark.asyncio
async def test_upload_attachment_file_too_large(client: AsyncClient, test_user, db_session):
    """Test attachment upload with file too large."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
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

    # Try to upload file larger than 10MB
    large_file_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.pdf", io.BytesIO(large_file_content), "application/pdf")}

    upload_response = await client.post(
        f"/api/v1/issues/{issue.id}/attachments",
        files=files,
        headers=auth_headers,
    )

    assert upload_response.status_code == 400
    error_data = upload_response.json()
    assert "exceeds maximum" in error_data.get("message", error_data.get("detail", "")).lower()


@pytest.mark.asyncio
async def test_download_attachment_success(client: AsyncClient, test_user, db_session):
    """Test successful attachment download."""
    # Setup
    org = OrganizationModel(name="Test Org", slug="test-org")
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=test_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    project = ProjectModel(organization_id=org.id, name="Test Project", key="TEST")
    db_session.add(project)
    await db_session.flush()

    issue = IssueModel(
        project_id=project.id,
        issue_number=1,
        title="Test Issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )
    db_session.add(issue)
    await db_session.flush()

    attachment = AttachmentModel(
        entity_type="issue",
        entity_id=issue.id,
        file_name="test_file.pdf",
        original_name="test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        storage_path="attachments/test/test_file.pdf",
        uploaded_by=test_user.id,
    )
    db_session.add(attachment)
    await db_session.flush()

    # Create the file in storage (for testing)
    from pathlib import Path

    from src.infrastructure.config import get_settings

    settings = get_settings()
    storage_path = Path(settings.storage_path) / attachment.storage_path
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(b"test file content")

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

    # Download attachment
    download_response = await client.get(
        f"/api/v1/attachments/{attachment.id}/download",
        headers=auth_headers,
    )

    assert download_response.status_code == 200
    assert download_response.content == b"test file content"
    assert download_response.headers["content-type"] == "application/pdf"
    assert 'attachment; filename="test.pdf"' in download_response.headers["content-disposition"]
