"""Unit tests for organization use cases."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from src.application.use_cases.organization import (
    CreateOrganizationUseCase,
    DeleteOrganizationUseCase,
    GetOrganizationUseCase,
    ListOrganizationsUseCase,
    UpdateOrganizationUseCase,
)
from src.domain.entities import Organization, User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


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


class TestCreateOrganizationUseCase:
    """Tests for CreateOrganizationUseCase."""

    @pytest.mark.asyncio
    async def test_create_organization_success(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test successful organization creation."""
        # Setup mocks
        request = CreateOrganizationRequest(
            name="New Organization", slug="new-org", description="Description"
        )
        mock_user_repository.get_by_id.return_value = test_user

        created_org = Organization.create(
            name=request.name,
            slug=request.slug,
            description=request.description,
        )
        mock_organization_repository.create.return_value = created_org
        mock_organization_repository.exists_by_slug.return_value = False

        # Mock OrganizationMemberModel add
        from unittest.mock import MagicMock

        MagicMock()
        mock_session.add = Mock()

        use_case = CreateOrganizationUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        # Execute
        result = await use_case.execute(request, str(test_user.id))

        # Assertions
        assert result.name == request.name
        assert result.slug == request.slug
        assert result.description == request.description
        assert result.member_count == 1
        mock_organization_repository.create.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_organization_user_not_found(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
    ):
        """Test organization creation fails when creator user not found."""
        request = CreateOrganizationRequest(name="New Organization")
        mock_user_repository.get_by_id.return_value = None

        use_case = CreateOrganizationUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request, str(uuid4()))

        mock_organization_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_organization_slug_conflict(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test organization creation fails when slug already exists."""
        request = CreateOrganizationRequest(name="New Organization", slug="existing-slug")
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.exists_by_slug.return_value = True
        mock_organization_repository.create.side_effect = ConflictException(
            "Slug already exists", field="slug"
        )

        use_case = CreateOrganizationUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ConflictException):
            await use_case.execute(request, str(test_user.id))


class TestGetOrganizationUseCase:
    """Tests for GetOrganizationUseCase."""

    @pytest.mark.asyncio
    async def test_get_organization_success(
        self, mock_organization_repository, mock_session, test_organization
    ):
        """Test successful organization retrieval."""
        mock_organization_repository.get_by_id.return_value = test_organization

        # Mock member count query
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.scalar_one = Mock(return_value=5)
        mock_session.execute = AsyncMock(return_value=mock_result)

        use_case = GetOrganizationUseCase(mock_organization_repository, mock_session)

        result = await use_case.execute(str(test_organization.id))

        assert result.id == test_organization.id
        assert result.name == test_organization.name
        assert result.member_count == 5

    @pytest.mark.asyncio
    async def test_get_organization_not_found(self, mock_organization_repository, mock_session):
        """Test get organization fails when not found."""
        mock_organization_repository.get_by_id.return_value = None

        use_case = GetOrganizationUseCase(mock_organization_repository, mock_session)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestListOrganizationsUseCase:
    """Tests for ListOrganizationsUseCase."""

    @pytest.mark.asyncio
    async def test_list_organizations_success(self, mock_organization_repository, mock_session):
        """Test successful organization listing."""
        org1 = Organization.create(name="Org 1", slug="org-1")
        org2 = Organization.create(name="Org 2", slug="org-2")
        mock_organization_repository.get_all.return_value = [org1, org2]
        mock_organization_repository.count.return_value = 2

        # Mock member count queries
        from unittest.mock import MagicMock

        mock_results = [
            MagicMock(scalar_one=Mock(return_value=3)),
            MagicMock(scalar_one=Mock(return_value=5)),
        ]
        mock_session.execute = AsyncMock(side_effect=mock_results)

        use_case = ListOrganizationsUseCase(mock_organization_repository, mock_session)

        user_id = str(uuid4())
        result = await use_case.execute(user_id, page=1, limit=20)

        assert len(result.organizations) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.limit == 20
        assert result.pages == 1

    @pytest.mark.asyncio
    async def test_list_organizations_with_search(self, mock_organization_repository, mock_session):
        """Test organization listing with search."""
        org = Organization.create(name="Test Org", slug="test-org")
        mock_organization_repository.search.return_value = [org]
        mock_organization_repository.count.return_value = 1

        # Mock member count query
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.scalar_one = Mock(return_value=2)
        mock_session.execute = AsyncMock(return_value=mock_result)

        use_case = ListOrganizationsUseCase(mock_organization_repository, mock_session)

        user_id = str(uuid4())
        result = await use_case.execute(user_id, page=1, limit=20, search="test")

        assert len(result.organizations) == 1
        assert result.total == 1
        mock_organization_repository.search.assert_called_once()


class TestUpdateOrganizationUseCase:
    """Tests for UpdateOrganizationUseCase."""

    @pytest.mark.asyncio
    async def test_update_organization_success(
        self, mock_organization_repository, mock_session, test_organization
    ):
        """Test successful organization update."""
        mock_organization_repository.get_by_id.return_value = test_organization
        updated_org = Organization.create(
            name="Updated Name", slug="updated-slug", description="Updated description"
        )
        updated_org.id = test_organization.id
        mock_organization_repository.update.return_value = updated_org

        # Mock member count query
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.scalar_one = Mock(return_value=4)
        mock_session.execute = AsyncMock(return_value=mock_result)

        use_case = UpdateOrganizationUseCase(mock_organization_repository, mock_session)

        request = UpdateOrganizationRequest(
            name="Updated Name", slug="updated-slug", description="Updated description"
        )
        result = await use_case.execute(str(test_organization.id), request)

        assert result.name == "Updated Name"
        assert result.slug == "updated-slug"
        mock_organization_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_organization_not_found(self, mock_organization_repository, mock_session):
        """Test update fails when organization not found."""
        mock_organization_repository.get_by_id.return_value = None

        use_case = UpdateOrganizationUseCase(mock_organization_repository, mock_session)

        request = UpdateOrganizationRequest(name="New Name")
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)


class TestDeleteOrganizationUseCase:
    """Tests for DeleteOrganizationUseCase."""

    @pytest.mark.asyncio
    async def test_delete_organization_success(
        self, mock_organization_repository, test_organization
    ):
        """Test successful organization deletion."""
        mock_organization_repository.get_by_id.return_value = test_organization
        test_organization.delete()
        mock_organization_repository.update.return_value = test_organization

        use_case = DeleteOrganizationUseCase(mock_organization_repository)

        await use_case.execute(str(test_organization.id))

        assert test_organization.deleted_at is not None
        mock_organization_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_organization_not_found(self, mock_organization_repository):
        """Test delete fails when organization not found."""
        mock_organization_repository.get_by_id.return_value = None

        use_case = DeleteOrganizationUseCase(mock_organization_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))
