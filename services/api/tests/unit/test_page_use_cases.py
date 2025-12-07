"""Unit tests for page use cases."""

from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.page import CreatePageRequest, UpdatePageRequest
from src.application.use_cases.page import (
    CreatePageUseCase,
    DeletePageUseCase,
    GetPageTreeUseCase,
    GetPageUseCase,
    ListPagesUseCase,
    UpdatePageUseCase,
)
from src.domain.entities import Page, Space, User
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
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session."""
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
    )


@pytest.fixture
def test_space():
    """Create a test space."""
    return Space.create(
        organization_id=uuid4(),
        name="Test Space",
        key="TEST",
        description="A test space",
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


class TestCreatePageUseCase:
    """Tests for CreatePageUseCase."""

    @pytest.mark.asyncio
    async def test_create_page_success(
        self,
        mock_page_repository,
        mock_space_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_space,
    ):
        """Test successful page creation."""
        request = CreatePageRequest(
            space_id=test_space.id,
            title="New Page",
            content="Page content",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_space_repository.get_by_id.return_value = test_space

        created_page = Page.create(
            space_id=request.space_id,
            title=request.title,
            content=request.content,
            created_by=test_user.id,
        )
        mock_page_repository.create.return_value = created_page
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreatePageUseCase(
            mock_page_repository,
            mock_space_repository,
            mock_user_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.title == "New Page"
        assert result.content == "Page content"
        assert result.space_id == test_space.id
        mock_page_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_with_parent(
        self,
        mock_page_repository,
        mock_space_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_space,
        test_page,
    ):
        """Test page creation with parent."""
        request = CreatePageRequest(
            space_id=test_space.id,
            title="Child Page",
            parent_id=test_page.id,
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_space_repository.get_by_id.return_value = test_space
        mock_page_repository.get_by_id.return_value = test_page

        created_page = Page.create(
            space_id=request.space_id,
            title=request.title,
            parent_id=request.parent_id,
            created_by=test_user.id,
        )
        mock_page_repository.create.return_value = created_page
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreatePageUseCase(
            mock_page_repository,
            mock_space_repository,
            mock_user_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.title == "Child Page"
        assert result.parent_id == test_page.id
        mock_page_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_space_not_found(
        self,
        mock_page_repository,
        mock_space_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test page creation fails when space not found."""
        request = CreatePageRequest(
            space_id=uuid4(),
            title="New Page",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_space_repository.get_by_id.return_value = None

        use_case = CreatePageUseCase(
            mock_page_repository,
            mock_space_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="Space"):
            await use_case.execute(request, str(test_user.id))


class TestGetPageUseCase:
    """Tests for GetPageUseCase."""

    @pytest.mark.asyncio
    async def test_get_page_success(self, mock_page_repository, mock_session, test_page):
        """Test successful page retrieval."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = GetPageUseCase(mock_page_repository, mock_session)

        result = await use_case.execute(str(test_page.id))

        assert result.id == test_page.id
        assert result.title == test_page.title
        mock_page_repository.get_by_id.assert_called_once_with(test_page.id)

    @pytest.mark.asyncio
    async def test_get_page_not_found(self, mock_page_repository, mock_session):
        """Test page retrieval fails when page not found."""
        page_id = uuid4()
        mock_page_repository.get_by_id.return_value = None

        use_case = GetPageUseCase(mock_page_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Page"):
            await use_case.execute(str(page_id))


class TestListPagesUseCase:
    """Tests for ListPagesUseCase."""

    @pytest.mark.asyncio
    async def test_list_pages_success(self, mock_page_repository, mock_session, test_space):
        """Test successful page listing."""
        page1 = Page.create(space_id=test_space.id, title="Page 1", created_by=uuid4())
        page2 = Page.create(space_id=test_space.id, title="Page 2", created_by=uuid4())

        mock_page_repository.get_all.return_value = [page1, page2]
        mock_page_repository.count.return_value = 2

        use_case = ListPagesUseCase(mock_page_repository, mock_session)

        result = await use_case.execute(str(test_space.id), page=1, limit=20)

        assert len(result.pages) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_pages_with_search(self, mock_page_repository, mock_session, test_space):
        """Test page listing with search query."""
        page = Page.create(space_id=test_space.id, title="Documentation Page", created_by=uuid4())

        mock_page_repository.search.return_value = [page]
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=1)))

        use_case = ListPagesUseCase(mock_page_repository, mock_session)

        result = await use_case.execute(
            str(test_space.id), page=1, limit=20, search="Documentation"
        )

        assert len(result.pages) == 1
        assert result.pages[0].title == "Documentation Page"
        mock_page_repository.search.assert_called_once()


class TestUpdatePageUseCase:
    """Tests for UpdatePageUseCase."""

    @pytest.mark.asyncio
    async def test_update_page_success(
        self, mock_page_repository, mock_session, test_page, test_user
    ):
        """Test successful page update."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        updated_page = Page.create(
            space_id=test_page.space_id,
            title="Updated Page",
            content="Updated content",
            created_by=test_page.created_by,
        )
        updated_page.id = test_page.id
        mock_page_repository.update.return_value = updated_page

        use_case = UpdatePageUseCase(mock_page_repository, mock_session)

        request = UpdatePageRequest(title="Updated Page", content="Updated content")
        result = await use_case.execute(str(test_page.id), request, str(test_user.id))

        assert result.title == "Updated Page"
        assert result.content == "Updated content"
        mock_page_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_page_not_found(self, mock_page_repository, mock_session, test_user):
        """Test page update fails when page not found."""
        page_id = uuid4()
        mock_page_repository.get_by_id.return_value = None

        use_case = UpdatePageUseCase(mock_page_repository, mock_session)

        request = UpdatePageRequest(title="Updated Page")
        with pytest.raises(EntityNotFoundException, match="Page"):
            await use_case.execute(str(page_id), request, str(test_user.id))


class TestDeletePageUseCase:
    """Tests for DeletePageUseCase."""

    @pytest.mark.asyncio
    async def test_delete_page_success(self, mock_page_repository, test_page):
        """Test successful page deletion."""
        mock_page_repository.get_by_id.return_value = test_page
        mock_page_repository.update = AsyncMock()

        use_case = DeletePageUseCase(mock_page_repository)

        await use_case.execute(str(test_page.id))

        assert test_page.deleted_at is not None
        mock_page_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_page_not_found(self, mock_page_repository):
        """Test page deletion fails when page not found."""
        page_id = uuid4()
        mock_page_repository.get_by_id.return_value = None

        use_case = DeletePageUseCase(mock_page_repository)

        with pytest.raises(EntityNotFoundException, match="Page"):
            await use_case.execute(str(page_id))


class TestGetPageTreeUseCase:
    """Tests for GetPageTreeUseCase."""

    @pytest.mark.asyncio
    async def test_get_page_tree_success(self, mock_page_repository, test_space):
        """Test successful page tree retrieval."""
        root_page = Page.create(space_id=test_space.id, title="Root Page", created_by=uuid4())
        child_page = Page.create(
            space_id=test_space.id, title="Child Page", parent_id=root_page.id, created_by=uuid4()
        )

        mock_page_repository.get_tree.return_value = [root_page, child_page]

        use_case = GetPageTreeUseCase(mock_page_repository)

        result = await use_case.execute(str(test_space.id))

        assert len(result.pages) == 1  # Only root pages
        assert result.pages[0].title == "Root Page"
        assert len(result.pages[0].children) == 1
        assert result.pages[0].children[0].title == "Child Page"
