"""Unit tests for page version use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.page_version import (
    CreatePageVersionUseCase,
    GetPageVersionDiffUseCase,
    GetPageVersionUseCase,
    ListPageVersionsUseCase,
    RestorePageVersionUseCase,
)
from src.domain.entities import Page, PageVersion, Space, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_page_repository():
    """Mock page repository."""
    return AsyncMock()


@pytest.fixture
def mock_page_version_repository():
    """Mock page version repository."""
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
    )


@pytest.fixture
def test_page_version(test_page, test_user):
    """Create a test page version."""
    return PageVersion.create(
        page_id=test_page.id,
        version_number=1,
        title="Test Page",
        content="Test content",
        created_by=test_user.id,
    )


class TestCreatePageVersionUseCase:
    """Tests for CreatePageVersionUseCase."""

    @pytest.mark.asyncio
    async def test_create_page_version_success(
        self, mock_page_repository, mock_page_version_repository, test_page, test_user
    ):
        """Test successful page version creation."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_version_repository.get_next_version_number.return_value = 1

        created_version = PageVersion.create(
            page_id=test_page.id,
            version_number=1,
            title=test_page.title,
            content=test_page.content,
            created_by=test_user.id,
        )
        mock_page_version_repository.create.return_value = created_version

        use_case = CreatePageVersionUseCase(mock_page_repository, mock_page_version_repository)
        result = await use_case.execute(str(test_page.id), created_by=str(test_user.id))

        assert result.version_number == 1
        assert result.title == test_page.title
        assert result.content == test_page.content
        mock_page_repository.get_by_id.assert_called_once()
        mock_page_version_repository.get_next_version_number.assert_called_once()
        mock_page_version_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_version_page_not_found(
        self, mock_page_repository, mock_page_version_repository
    ):
        """Test page version creation when page not found."""
        mock_page_repository.get_by_id.return_value = None

        use_case = CreatePageVersionUseCase(mock_page_repository, mock_page_version_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestListPageVersionsUseCase:
    """Tests for ListPageVersionsUseCase."""

    @pytest.mark.asyncio
    async def test_list_page_versions_success(
        self, mock_page_repository, mock_page_version_repository, test_page, test_page_version
    ):
        """Test successful page version listing."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_version_repository.get_all.return_value = [test_page_version]
        mock_page_version_repository.count.return_value = 1

        use_case = ListPageVersionsUseCase(mock_page_repository, mock_page_version_repository)
        result = await use_case.execute(str(test_page.id), page=1, limit=20)

        assert result.total == 1
        assert len(result.versions) == 1
        assert result.versions[0].version_number == 1

    @pytest.mark.asyncio
    async def test_list_page_versions_page_not_found(
        self, mock_page_repository, mock_page_version_repository
    ):
        """Test page version listing when page not found."""
        mock_page_repository.get_by_id.return_value = None

        use_case = ListPageVersionsUseCase(mock_page_repository, mock_page_version_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestGetPageVersionUseCase:
    """Tests for GetPageVersionUseCase."""

    @pytest.mark.asyncio
    async def test_get_page_version_success(self, mock_page_version_repository, test_page_version):
        """Test successful page version retrieval."""
        mock_page_version_repository.get_by_id.return_value = test_page_version

        use_case = GetPageVersionUseCase(mock_page_version_repository)
        result = await use_case.execute(str(test_page_version.id))

        assert result.version_number == 1
        assert result.title == test_page_version.title

    @pytest.mark.asyncio
    async def test_get_page_version_not_found(self, mock_page_version_repository):
        """Test page version retrieval when version not found."""
        mock_page_version_repository.get_by_id.return_value = None

        use_case = GetPageVersionUseCase(mock_page_version_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestRestorePageVersionUseCase:
    """Tests for RestorePageVersionUseCase."""

    @pytest.mark.asyncio
    async def test_restore_page_version_success(
        self,
        mock_page_repository,
        mock_page_version_repository,
        test_page,
        test_page_version,
        test_user,
    ):
        """Test successful page version restoration."""
        mock_page_version_repository.get_by_id.return_value = test_page_version
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_version_repository.get_next_version_number.return_value = 2

        updated_page = Page.create(
            space_id=test_page.space_id,
            title=test_page_version.title,
            content=test_page_version.content,
            created_by=test_user.id,
        )
        updated_page.id = test_page.id
        mock_page_repository.update.return_value = updated_page

        new_version = PageVersion.create(
            page_id=test_page.id,
            version_number=2,
            title=test_page_version.title,
            content=test_page_version.content,
            created_by=test_user.id,
        )
        mock_page_version_repository.create.return_value = new_version

        use_case = RestorePageVersionUseCase(mock_page_repository, mock_page_version_repository)
        result = await use_case.execute(str(test_page_version.id), restored_by=str(test_user.id))

        assert result.page_id == test_page.id
        assert result.restored_version_id == test_page_version.id
        assert result.new_version_id == new_version.id

    @pytest.mark.asyncio
    async def test_restore_page_version_not_found(
        self, mock_page_repository, mock_page_version_repository
    ):
        """Test page version restoration when version not found."""
        mock_page_version_repository.get_by_id.return_value = None

        use_case = RestorePageVersionUseCase(mock_page_repository, mock_page_version_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestGetPageVersionDiffUseCase:
    """Tests for GetPageVersionDiffUseCase."""

    @pytest.mark.asyncio
    async def test_get_page_version_diff_with_current_page(
        self,
        mock_page_repository,
        mock_page_version_repository,
        test_page,
        test_page_version,
    ):
        """Test getting diff between version and current page."""
        mock_page_version_repository.get_by_id.return_value = test_page_version
        mock_page_repository.get_by_id.return_value = test_page

        use_case = GetPageVersionDiffUseCase(mock_page_repository, mock_page_version_repository)
        result = await use_case.execute(str(test_page_version.id), compare_to_version_id=None)

        assert result.version_id == test_page_version.id
        assert result.version_number == 1
        assert result.compare_to_version_number is None

    @pytest.mark.asyncio
    async def test_get_page_version_diff_with_another_version(
        self,
        mock_page_repository,
        mock_page_version_repository,
        test_page,
        test_page_version,
    ):
        """Test getting diff between two versions."""
        compare_version = PageVersion.create(
            page_id=test_page.id,
            version_number=2,
            title="Updated Title",
            content="Updated content",
            created_by=test_page_version.created_by,
        )

        mock_page_version_repository.get_by_id.side_effect = [
            test_page_version,
            compare_version,
        ]

        use_case = GetPageVersionDiffUseCase(mock_page_repository, mock_page_version_repository)
        result = await use_case.execute(
            str(test_page_version.id), compare_to_version_id=str(compare_version.id)
        )

        assert result.version_id == test_page_version.id
        assert result.compare_to_version_id == compare_version.id
        assert result.version_number == 1
        assert result.compare_to_version_number == 2

    @pytest.mark.asyncio
    async def test_get_page_version_diff_version_not_found(
        self, mock_page_repository, mock_page_version_repository
    ):
        """Test getting diff when version not found."""
        mock_page_version_repository.get_by_id.return_value = None

        use_case = GetPageVersionDiffUseCase(mock_page_repository, mock_page_version_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
