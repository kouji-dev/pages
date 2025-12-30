"""Unit tests for favorite use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.favorite import CreateFavoriteRequest
from src.application.use_cases.favorite import (
    CreateFavoriteUseCase,
    DeleteFavoriteUseCase,
    ListFavoritesUseCase,
)
from src.domain.entities import Favorite, Project, Space, User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects import Email, EntityType, HashedPassword


@pytest.fixture
def mock_favorite_repository():
    """Mock favorite repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


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
def test_favorite(test_user):
    """Create a test favorite."""
    return Favorite.create(
        user_id=test_user.id,
        entity_type=EntityType.project(),
        entity_id=uuid4(),
    )


class TestCreateFavoriteUseCase:
    """Tests for CreateFavoriteUseCase."""

    @pytest.mark.asyncio
    async def test_create_favorite_success(
        self, mock_favorite_repository, mock_user_repository, test_user
    ):
        """Test successful favorite creation."""
        entity_id = uuid4()
        request = CreateFavoriteRequest(
            entity_type="project",
            entity_id=entity_id,
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_favorite_repository.exists.return_value = False

        created_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.project(),
            entity_id=entity_id,
        )
        mock_favorite_repository.create.return_value = created_favorite

        use_case = CreateFavoriteUseCase(mock_favorite_repository, mock_user_repository)

        result = await use_case.execute(request, str(test_user.id))

        assert result.entity_type == "project"
        assert result.entity_id == entity_id
        assert result.user_id == test_user.id
        mock_favorite_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_favorite_space(
        self, mock_favorite_repository, mock_user_repository, test_user
    ):
        """Test favorite creation for space."""
        entity_id = uuid4()
        request = CreateFavoriteRequest(
            entity_type="space",
            entity_id=entity_id,
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_favorite_repository.exists.return_value = False

        created_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.space(),
            entity_id=entity_id,
        )
        mock_favorite_repository.create.return_value = created_favorite

        use_case = CreateFavoriteUseCase(mock_favorite_repository, mock_user_repository)

        result = await use_case.execute(request, str(test_user.id))

        assert result.entity_type == "space"
        assert result.entity_id == entity_id

    @pytest.mark.asyncio
    async def test_create_favorite_page(
        self, mock_favorite_repository, mock_user_repository, test_user
    ):
        """Test favorite creation for page."""
        entity_id = uuid4()
        request = CreateFavoriteRequest(
            entity_type="page",
            entity_id=entity_id,
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_favorite_repository.exists.return_value = False

        created_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.page(),
            entity_id=entity_id,
        )
        mock_favorite_repository.create.return_value = created_favorite

        use_case = CreateFavoriteUseCase(mock_favorite_repository, mock_user_repository)

        result = await use_case.execute(request, str(test_user.id))

        assert result.entity_type == "page"
        assert result.entity_id == entity_id

    @pytest.mark.asyncio
    async def test_create_favorite_user_not_found(
        self, mock_favorite_repository, mock_user_repository
    ):
        """Test favorite creation with non-existent user."""
        request = CreateFavoriteRequest(
            entity_type="project",
            entity_id=uuid4(),
        )
        mock_user_repository.get_by_id.return_value = None

        use_case = CreateFavoriteUseCase(mock_favorite_repository, mock_user_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request, str(uuid4()))

    @pytest.mark.asyncio
    async def test_create_favorite_already_exists(
        self, mock_favorite_repository, mock_user_repository, test_user
    ):
        """Test favorite creation when favorite already exists."""
        entity_id = uuid4()
        request = CreateFavoriteRequest(
            entity_type="project",
            entity_id=entity_id,
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_favorite_repository.exists.return_value = True

        use_case = CreateFavoriteUseCase(mock_favorite_repository, mock_user_repository)

        with pytest.raises(ConflictException):
            await use_case.execute(request, str(test_user.id))

    @pytest.mark.asyncio
    async def test_create_favorite_invalid_entity_type(
        self, mock_favorite_repository, mock_user_repository, test_user
    ):
        """Test favorite creation with invalid entity type."""
        # Pydantic validates Literal before our validator runs
        # So we expect a Pydantic ValidationError, not our ValidationException
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateFavoriteRequest(
                entity_type="invalid",
                entity_id=uuid4(),
            )


class TestListFavoritesUseCase:
    """Tests for ListFavoritesUseCase."""

    @pytest.mark.asyncio
    async def test_list_favorites_success(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
        test_favorite,
    ):
        """Test successful favorite listing."""
        favorites = [test_favorite]
        mock_favorite_repository.get_all.return_value = favorites
        mock_favorite_repository.count.return_value = 1
        # Mock project repository for project favorite
        project_id = test_favorite.entity_id
        project = Project(
            id=project_id,
            organization_id=uuid4(),
            name="Test Project",
            key="TEST",
        )
        mock_project_repository.get_by_id.return_value = project
        # Mock session queries - create separate mock results for each query
        folder_result = AsyncMock()
        folder_result.scalar_one_or_none = lambda: None
        member_result = AsyncMock()
        member_result.scalar_one = lambda: 0
        issue_result = AsyncMock()
        issue_result.scalar_one = lambda: 0
        # Return different results for different queries
        mock_session.execute.side_effect = [folder_result, member_result, issue_result]

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id))

        assert len(result.favorites) == 1
        assert result.favorites[0].id == test_favorite.id
        assert result.favorites[0].node is not None
        assert result.favorites[0].node.type == "project"
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_favorites_with_entity_type_filter(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
    ):
        """Test favorite listing with entity type filter."""
        project_id = uuid4()
        project_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.project(),
            entity_id=project_id,
        )
        favorites = [project_favorite]
        mock_favorite_repository.get_all.return_value = favorites
        mock_favorite_repository.count.return_value = 1
        # Mock project repository
        project = Project(
            id=project_id,
            organization_id=uuid4(),
            name="Test Project",
            key="TEST",
        )
        mock_project_repository.get_by_id.return_value = project
        # Mock session queries - create separate mock results for each query
        folder_result = AsyncMock()
        folder_result.scalar_one_or_none = lambda: None
        member_result = AsyncMock()
        member_result.scalar_one = lambda: 0
        issue_result = AsyncMock()
        issue_result.scalar_one = lambda: 0
        # Return different results for different queries
        mock_session.execute.side_effect = [folder_result, member_result, issue_result]

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id), entity_type="project")

        assert len(result.favorites) == 1
        assert result.favorites[0].entity_type == "project"
        assert result.favorites[0].node is not None

    @pytest.mark.asyncio
    async def test_list_favorites_empty(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
    ):
        """Test favorite listing with no favorites."""
        mock_favorite_repository.get_all.return_value = []
        mock_favorite_repository.count.return_value = 0

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id))

        assert len(result.favorites) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_favorites_with_pagination(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
    ):
        """Test favorite listing with pagination."""
        favorites = [
            Favorite.create(
                user_id=test_user.id,
                entity_type=EntityType.project(),
                entity_id=uuid4(),
            )
            for _ in range(5)
        ]
        mock_favorite_repository.get_all.return_value = favorites
        mock_favorite_repository.count.return_value = 10
        # Mock project repository for all favorites
        mock_project_repository.get_by_id.return_value = Project(
            id=uuid4(),
            organization_id=uuid4(),
            name="Test Project",
            key="TEST",
        )
        # Mock session queries - need to return multiple results for each favorite
        folder_result = AsyncMock()
        folder_result.scalar_one_or_none = lambda: None
        member_result = AsyncMock()
        member_result.scalar_one = lambda: 0
        issue_result = AsyncMock()
        issue_result.scalar_one = lambda: 0
        # Return results for each favorite (5 favorites * 3 queries each = 15 results)
        mock_session.execute.side_effect = [
            folder_result,
            member_result,
            issue_result,
        ] * 5

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id), skip=0, limit=5)

        assert len(result.favorites) == 5
        assert result.total == 10

    @pytest.mark.asyncio
    async def test_list_favorites_with_space(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
    ):
        """Test favorite listing with space favorite."""
        space_id = uuid4()
        space_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.space(),
            entity_id=space_id,
        )
        favorites = [space_favorite]
        mock_favorite_repository.get_all.return_value = favorites
        mock_favorite_repository.count.return_value = 1
        # Mock space repository
        space = Space(
            id=space_id,
            organization_id=uuid4(),
            name="Test Space",
            key="TEST",
        )
        mock_space_repository.get_by_id.return_value = space
        # Mock session queries
        folder_result = AsyncMock()
        folder_result.scalar_one_or_none = lambda: None
        page_count_result = AsyncMock()
        page_count_result.scalar_one = lambda: 0
        mock_session.execute.side_effect = [folder_result, page_count_result]

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id))

        assert len(result.favorites) == 1
        assert result.favorites[0].entity_type == "space"
        assert result.favorites[0].node is not None
        assert result.favorites[0].node.type == "space"

    @pytest.mark.asyncio
    async def test_list_favorites_with_page(
        self,
        mock_favorite_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_user,
    ):
        """Test favorite listing with page favorite (node should be None)."""
        page_id = uuid4()
        page_favorite = Favorite.create(
            user_id=test_user.id,
            entity_type=EntityType.page(),
            entity_id=page_id,
        )
        favorites = [page_favorite]
        mock_favorite_repository.get_all.return_value = favorites
        mock_favorite_repository.count.return_value = 1

        use_case = ListFavoritesUseCase(
            mock_favorite_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_user.id))

        assert len(result.favorites) == 1
        assert result.favorites[0].entity_type == "page"
        assert result.favorites[0].node is None


class TestDeleteFavoriteUseCase:
    """Tests for DeleteFavoriteUseCase."""

    @pytest.mark.asyncio
    async def test_delete_favorite_success(self, mock_favorite_repository, test_favorite):
        """Test successful favorite deletion."""
        mock_favorite_repository.get_by_id.return_value = test_favorite
        mock_favorite_repository.delete = AsyncMock()

        use_case = DeleteFavoriteUseCase(mock_favorite_repository)

        await use_case.execute(str(test_favorite.id))

        mock_favorite_repository.delete.assert_called_once_with(test_favorite.id)

    @pytest.mark.asyncio
    async def test_delete_favorite_not_found(self, mock_favorite_repository):
        """Test favorite deletion with non-existent ID."""
        mock_favorite_repository.get_by_id.return_value = None

        use_case = DeleteFavoriteUseCase(mock_favorite_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
