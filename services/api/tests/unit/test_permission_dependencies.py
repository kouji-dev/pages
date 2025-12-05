"""Tests for permission dependencies."""

import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.domain.entities import User
from src.domain.value_objects import Email, HashedPassword, Role
from src.application.services.permission_service import PermissionService
from src.presentation.dependencies.permissions import (
    get_organization_role,
    require_edit_permission,
    require_organization_admin,
    require_organization_member,
    require_project_access,
)


@pytest.fixture
def test_user() -> User:
    """Create a test user."""
    # Use a valid bcrypt hash
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User.create(
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
    )


@pytest.fixture
def permission_service() -> MagicMock:
    """Create a mock permission service."""
    return MagicMock(spec=PermissionService)


class TestRequireOrganizationMember:
    """Tests for require_organization_member dependency."""

    @pytest.mark.asyncio
    async def test_require_organization_member_success(self, test_user, permission_service) -> None:
        """Test successful organization member check."""
        organization_id = uuid4()
        permission_service.can_access_organization = AsyncMock(return_value=True)

        result = await require_organization_member(
            organization_id=organization_id,
            current_user=test_user,
            permission_service=permission_service,
        )

        assert result == test_user
        permission_service.can_access_organization.assert_called_once_with(
            test_user, organization_id
        )

    @pytest.mark.asyncio
    async def test_require_organization_member_denied(self, test_user, permission_service) -> None:
        """Test organization member check failure."""
        organization_id = uuid4()
        permission_service.can_access_organization = AsyncMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_organization_member(
                organization_id=organization_id,
                current_user=test_user,
                permission_service=permission_service,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not a member" in exc_info.value.detail.lower()


class TestRequireOrganizationAdmin:
    """Tests for require_organization_admin dependency."""

    @pytest.mark.asyncio
    async def test_require_organization_admin_success(self, test_user, permission_service) -> None:
        """Test successful organization admin check."""
        organization_id = uuid4()
        permission_service.can_manage_organization = AsyncMock(return_value=True)

        result = await require_organization_admin(
            organization_id=organization_id,
            current_user=test_user,
            permission_service=permission_service,
        )

        assert result == test_user
        permission_service.can_manage_organization.assert_called_once_with(
            test_user, organization_id
        )

    @pytest.mark.asyncio
    async def test_require_organization_admin_denied(self, test_user, permission_service) -> None:
        """Test organization admin check failure."""
        organization_id = uuid4()
        permission_service.can_manage_organization = AsyncMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_organization_admin(
                organization_id=organization_id,
                current_user=test_user,
                permission_service=permission_service,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "admin" in exc_info.value.detail.lower()


class TestRequireProjectAccess:
    """Tests for require_project_access dependency."""

    @pytest.mark.asyncio
    async def test_require_project_access_success(self, test_user, permission_service) -> None:
        """Test successful project access check."""
        project_id = uuid4()
        permission_service.can_access_project = AsyncMock(return_value=True)

        result = await require_project_access(
            project_id=project_id,
            current_user=test_user,
            permission_service=permission_service,
        )

        assert result == test_user
        permission_service.can_access_project.assert_called_once_with(test_user, project_id)

    @pytest.mark.asyncio
    async def test_require_project_access_denied(self, test_user, permission_service) -> None:
        """Test project access check failure."""
        project_id = uuid4()
        permission_service.can_access_project = AsyncMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_project_access(
                project_id=project_id,
                current_user=test_user,
                permission_service=permission_service,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "access" in exc_info.value.detail.lower()


class TestRequireEditPermission:
    """Tests for require_edit_permission dependency."""

    @pytest.mark.asyncio
    async def test_require_edit_permission_success_no_project(
        self, test_user, permission_service
    ) -> None:
        """Test successful edit permission check without project."""
        organization_id = uuid4()
        permission_service.can_edit_content = AsyncMock(return_value=True)

        result = await require_edit_permission(
            organization_id=organization_id,
            current_user=test_user,
            permission_service=permission_service,
            project_id=None,
        )

        assert result == test_user
        permission_service.can_edit_content.assert_called_once_with(
            test_user, organization_id, None
        )

    @pytest.mark.asyncio
    async def test_require_edit_permission_success_with_project(
        self, test_user, permission_service
    ) -> None:
        """Test successful edit permission check with project."""
        organization_id = uuid4()
        project_id = uuid4()
        permission_service.can_edit_content = AsyncMock(return_value=True)

        result = await require_edit_permission(
            organization_id=organization_id,
            current_user=test_user,
            permission_service=permission_service,
            project_id=project_id,
        )

        assert result == test_user
        permission_service.can_edit_content.assert_called_once_with(
            test_user, organization_id, project_id
        )

    @pytest.mark.asyncio
    async def test_require_edit_permission_denied(self, test_user, permission_service) -> None:
        """Test edit permission check failure."""
        organization_id = uuid4()
        permission_service.can_edit_content = AsyncMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await require_edit_permission(
                organization_id=organization_id,
                current_user=test_user,
                permission_service=permission_service,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert (
            "permission" in exc_info.value.detail.lower() or "edit" in exc_info.value.detail.lower()
        )


class TestGetOrganizationRole:
    """Tests for get_organization_role dependency."""

    @pytest.mark.asyncio
    async def test_get_organization_role_success(self, test_user, permission_service) -> None:
        """Test successful organization role retrieval."""
        organization_id = uuid4()
        permission_service.get_organization_role = AsyncMock(return_value=Role.ADMIN)

        result = await get_organization_role(
            organization_id=organization_id,
            current_user=test_user,
            permission_service=permission_service,
        )

        assert result == Role.ADMIN
        permission_service.get_organization_role.assert_called_once_with(
            test_user.id, organization_id
        )

    @pytest.mark.asyncio
    async def test_get_organization_role_not_member(self, test_user, permission_service) -> None:
        """Test organization role retrieval when not a member."""
        organization_id = uuid4()
        permission_service.get_organization_role = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_organization_role(
                organization_id=organization_id,
                current_user=test_user,
                permission_service=permission_service,
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "not a member" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_organization_role_returns_all_roles(
        self, test_user, permission_service
    ) -> None:
        """Test organization role retrieval returns all role types."""
        organization_id = uuid4()

        for role in [Role.ADMIN, Role.MEMBER, Role.VIEWER]:
            permission_service.get_organization_role = AsyncMock(return_value=role)

            result = await get_organization_role(
                organization_id=organization_id,
                current_user=test_user,
                permission_service=permission_service,
            )

            assert result == role
