"""Unit tests for space use cases."""

from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.space import CreateSpaceRequest, UpdateSpaceRequest
from src.application.use_cases.space import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    GetSpaceUseCase,
    ListSpacesUseCase,
    UpdateSpaceUseCase,
)
from src.domain.entities import Organization, Space, User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def mock_organization_repository():
    """Mock organization repository."""
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
def test_organization():
    """Create a test organization."""
    return Organization.create(
        name="Test Organization",
        slug="test-org",
        description="A test organization",
    )


@pytest.fixture
def test_space(test_organization):
    """Create a test space."""
    return Space.create(
        organization_id=test_organization.id,
        name="Test Space",
        key="TEST",
        description="A test space",
    )


class TestCreateSpaceUseCase:
    """Tests for CreateSpaceUseCase."""

    @pytest.mark.asyncio
    async def test_create_space_success(
        self,
        mock_space_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test successful space creation."""
        request = CreateSpaceRequest(
            organization_id=test_organization.id,
            name="New Space",
            key="NEW",
            description="Description",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization

        created_space = Space.create(
            organization_id=request.organization_id,
            name=request.name,
            key=request.key,
            description=request.description,
        )
        mock_space_repository.create.return_value = created_space
        mock_space_repository.exists_by_key.return_value = False

        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreateSpaceUseCase(
            mock_space_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.name == "New Space"
        assert result.key == "NEW"
        assert result.description == "Description"
        assert result.organization_id == test_organization.id
        mock_space_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_space_auto_key(
        self,
        mock_space_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test space creation with auto-generated key."""
        request = CreateSpaceRequest(
            organization_id=test_organization.id,
            name="My Awesome Space",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization

        created_space = Space.create(
            organization_id=request.organization_id,
            name=request.name,
        )
        mock_space_repository.create.return_value = created_space
        mock_space_repository.exists_by_key.return_value = False

        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreateSpaceUseCase(
            mock_space_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.name == "My Awesome Space"
        assert result.key == "MYAWESOMES"  # Auto-generated from name (max 10 chars)
        mock_space_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_space_organization_not_found(
        self,
        mock_space_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test space creation fails when organization not found."""
        request = CreateSpaceRequest(
            organization_id=uuid4(),
            name="New Space",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = None

        use_case = CreateSpaceUseCase(
            mock_space_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="Organization"):
            await use_case.execute(request, str(test_user.id))

    @pytest.mark.asyncio
    async def test_create_space_key_conflict(
        self,
        mock_space_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test space creation fails with duplicate key in organization."""
        request = CreateSpaceRequest(
            organization_id=test_organization.id,
            name="New Space",
            key="TEST",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_space_repository.create.side_effect = ConflictException(
            "Space with key 'TEST' already exists in this organization", field="key"
        )

        use_case = CreateSpaceUseCase(
            mock_space_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(ConflictException):
            await use_case.execute(request, str(test_user.id))


class TestGetSpaceUseCase:
    """Tests for GetSpaceUseCase."""

    @pytest.mark.asyncio
    async def test_get_space_success(self, mock_space_repository, mock_session, test_space):
        """Test successful space retrieval."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = GetSpaceUseCase(mock_space_repository, mock_session)

        result = await use_case.execute(str(test_space.id))

        assert result.id == test_space.id
        assert result.name == test_space.name
        assert result.key == test_space.key
        mock_space_repository.get_by_id.assert_called_once_with(test_space.id)

    @pytest.mark.asyncio
    async def test_get_space_not_found(self, mock_space_repository, mock_session):
        """Test space retrieval fails when space not found."""
        space_id = uuid4()
        mock_space_repository.get_by_id.return_value = None

        use_case = GetSpaceUseCase(mock_space_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Space"):
            await use_case.execute(str(space_id))


class TestListSpacesUseCase:
    """Tests for ListSpacesUseCase."""

    @pytest.mark.asyncio
    async def test_list_spaces_success(
        self, mock_space_repository, mock_session, test_organization
    ):
        """Test successful space listing."""
        space1 = Space.create(organization_id=test_organization.id, name="Space 1", key="SPACE1")
        space2 = Space.create(organization_id=test_organization.id, name="Space 2", key="SPACE2")

        mock_space_repository.get_all.return_value = [space1, space2]
        mock_space_repository.count.return_value = 2
        mock_session.execute = AsyncMock(
            return_value=MagicMock(scalar_one=Mock(side_effect=[0, 0]))
        )

        use_case = ListSpacesUseCase(mock_space_repository, mock_session)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20)

        assert len(result.spaces) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_spaces_with_search(
        self, mock_space_repository, mock_session, test_organization
    ):
        """Test space listing with search query."""
        space = Space.create(
            organization_id=test_organization.id, name="Documentation Space", key="DOC"
        )

        mock_space_repository.search.return_value = [space]
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=1)))

        use_case = ListSpacesUseCase(mock_space_repository, mock_session)

        result = await use_case.execute(
            str(test_organization.id), page=1, limit=20, search="Documentation"
        )

        assert len(result.spaces) == 1
        assert result.spaces[0].name == "Documentation Space"
        mock_space_repository.search.assert_called_once()


class TestUpdateSpaceUseCase:
    """Tests for UpdateSpaceUseCase."""

    @pytest.mark.asyncio
    async def test_update_space_success(self, mock_space_repository, mock_session, test_space):
        """Test successful space update."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        updated_space = Space.create(
            organization_id=test_space.organization_id,
            name="Updated Space",
            key=test_space.key,
            description="Updated description",
        )
        updated_space.id = test_space.id
        mock_space_repository.update.return_value = updated_space

        use_case = UpdateSpaceUseCase(mock_space_repository, mock_session)

        request = UpdateSpaceRequest(name="Updated Space", description="Updated description")
        result = await use_case.execute(str(test_space.id), request)

        assert result.name == "Updated Space"
        assert result.description == "Updated description"
        mock_space_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_space_not_found(self, mock_space_repository, mock_session):
        """Test space update fails when space not found."""
        space_id = uuid4()
        mock_space_repository.get_by_id.return_value = None

        use_case = UpdateSpaceUseCase(mock_space_repository, mock_session)

        request = UpdateSpaceRequest(name="Updated Space")
        with pytest.raises(EntityNotFoundException, match="Space"):
            await use_case.execute(str(space_id), request)


class TestDeleteSpaceUseCase:
    """Tests for DeleteSpaceUseCase."""

    @pytest.mark.asyncio
    async def test_delete_space_success(self, mock_space_repository, test_space):
        """Test successful space deletion."""
        mock_space_repository.get_by_id.return_value = test_space
        mock_space_repository.update = AsyncMock()

        use_case = DeleteSpaceUseCase(mock_space_repository)

        await use_case.execute(str(test_space.id))

        assert test_space.deleted_at is not None
        mock_space_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_space_not_found(self, mock_space_repository):
        """Test space deletion fails when space not found."""
        space_id = uuid4()
        mock_space_repository.get_by_id.return_value = None

        use_case = DeleteSpaceUseCase(mock_space_repository)

        with pytest.raises(EntityNotFoundException, match="Space"):
            await use_case.execute(str(space_id))
