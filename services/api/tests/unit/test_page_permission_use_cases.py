"""Unit tests for page permission use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.page_permission import (
    UpdatePagePermissionRequest,
    UpdateSpacePermissionRequest,
)
from src.application.use_cases.page_permission import (
    GetPagePermissionsUseCase,
    GetSpacePermissionsUseCase,
    UpdatePagePermissionsUseCase,
    UpdateSpacePermissionsUseCase,
)
from src.domain.entities import Page, PagePermission, Space, SpacePermission, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_page_repository():
    """Mock page repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def mock_page_permission_repository():
    """Mock page permission repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_permission_repository():
    """Mock space permission repository."""
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
def test_page_permission(test_page, test_user):
    """Create a test page permission."""
    return PagePermission.create(
        page_id=test_page.id,
        user_id=test_user.id,
        role="edit",
    )


@pytest.fixture
def test_space_permission(test_space, test_user):
    """Create a test space permission."""
    return SpacePermission.create(
        space_id=test_space.id,
        user_id=test_user.id,
        role="edit",
    )


class TestGetPagePermissionsUseCase:
    """Tests for GetPagePermissionsUseCase."""

    @pytest.mark.asyncio
    async def test_get_page_permissions_success(
        self,
        mock_page_repository,
        mock_page_permission_repository,
        test_page,
        test_page_permission,
    ):
        """Test successful page permissions retrieval."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_permission_repository.get_all_by_page.return_value = [test_page_permission]

        use_case = GetPagePermissionsUseCase(mock_page_repository, mock_page_permission_repository)
        result = await use_case.execute(str(test_page.id))

        assert result.total == 1
        assert len(result.permissions) == 1
        assert result.permissions[0].role == "edit"

    @pytest.mark.asyncio
    async def test_get_page_permissions_page_not_found(
        self, mock_page_repository, mock_page_permission_repository
    ):
        """Test page permissions retrieval when page not found."""
        mock_page_repository.get_by_id.return_value = None

        use_case = GetPagePermissionsUseCase(mock_page_repository, mock_page_permission_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdatePagePermissionsUseCase:
    """Tests for UpdatePagePermissionsUseCase."""

    @pytest.mark.asyncio
    async def test_update_page_permissions_success(
        self,
        mock_page_repository,
        mock_page_permission_repository,
        test_page,
        test_user,
    ):
        """Test successful page permissions update."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_permission_repository.get_all_by_page.return_value = []

        new_permission = PagePermission.create(
            page_id=test_page.id,
            user_id=test_user.id,
            role="admin",
        )
        mock_page_permission_repository.create.return_value = new_permission

        request = UpdatePagePermissionRequest(
            permissions=[{"user_id": str(test_user.id), "role": "admin"}]
        )

        use_case = UpdatePagePermissionsUseCase(
            mock_page_repository, mock_page_permission_repository
        )
        result = await use_case.execute(str(test_page.id), request)

        assert result.total == 1
        assert result.permissions[0].role == "admin"

    @pytest.mark.asyncio
    async def test_update_page_permissions_page_not_found(
        self, mock_page_repository, mock_page_permission_repository
    ):
        """Test page permissions update when page not found."""
        mock_page_repository.get_by_id.return_value = None

        request = UpdatePagePermissionRequest(permissions=[])

        use_case = UpdatePagePermissionsUseCase(
            mock_page_repository, mock_page_permission_repository
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)


class TestGetSpacePermissionsUseCase:
    """Tests for GetSpacePermissionsUseCase."""

    @pytest.mark.asyncio
    async def test_get_space_permissions_success(
        self,
        mock_space_repository,
        mock_space_permission_repository,
        test_space,
        test_space_permission,
    ):
        """Test successful space permissions retrieval."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_space_permission_repository.get_all_by_space.return_value = [test_space_permission]

        use_case = GetSpacePermissionsUseCase(
            mock_space_repository, mock_space_permission_repository
        )
        result = await use_case.execute(str(test_space.id))

        assert result.total == 1
        assert len(result.permissions) == 1
        assert result.permissions[0].role == "edit"

    @pytest.mark.asyncio
    async def test_get_space_permissions_space_not_found(
        self, mock_space_repository, mock_space_permission_repository
    ):
        """Test space permissions retrieval when space not found."""
        mock_space_repository.get_by_id.return_value = None

        use_case = GetSpacePermissionsUseCase(
            mock_space_repository, mock_space_permission_repository
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdateSpacePermissionsUseCase:
    """Tests for UpdateSpacePermissionsUseCase."""

    @pytest.mark.asyncio
    async def test_update_space_permissions_success(
        self,
        mock_space_repository,
        mock_space_permission_repository,
        test_space,
        test_user,
    ):
        """Test successful space permissions update."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_space_permission_repository.get_all_by_space.return_value = []

        new_permission = SpacePermission.create(
            space_id=test_space.id,
            user_id=test_user.id,
            role="admin",
        )
        mock_space_permission_repository.create.return_value = new_permission

        request = UpdateSpacePermissionRequest(
            permissions=[{"user_id": str(test_user.id), "role": "admin"}]
        )

        use_case = UpdateSpacePermissionsUseCase(
            mock_space_repository, mock_space_permission_repository
        )
        result = await use_case.execute(str(test_space.id), request)

        assert result.total == 1
        assert result.permissions[0].role == "admin"

    @pytest.mark.asyncio
    async def test_update_space_permissions_space_not_found(
        self, mock_space_repository, mock_space_permission_repository
    ):
        """Test space permissions update when space not found."""
        mock_space_repository.get_by_id.return_value = None

        request = UpdateSpacePermissionRequest(permissions=[])

        use_case = UpdateSpacePermissionsUseCase(
            mock_space_repository, mock_space_permission_repository
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)
