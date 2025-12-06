"""Unit tests for organization member use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.organization_member import (
    AddMemberRequest,
    UpdateMemberRoleRequest,
)
from src.application.use_cases.organization import (
    AddOrganizationMemberUseCase,
    ListOrganizationMembersUseCase,
    RemoveOrganizationMemberUseCase,
    UpdateOrganizationMemberRoleUseCase,
)
from src.domain.entities import Organization, User
from src.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from src.domain.value_objects import Email, HashedPassword, Role


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
def test_organization():
    """Create a test organization."""
    return Organization.create(
        name="Test Organization",
        slug="test-org",
    )


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
def another_user():
    """Create another test user."""
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("another@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Another User",
    )


class TestAddOrganizationMemberUseCase:
    """Tests for AddOrganizationMemberUseCase."""

    @pytest.mark.asyncio
    async def test_add_member_success(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test successful member addition."""
        request = AddMemberRequest(user_id=test_user.id, role="member")
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        # Mock no existing member
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        # Mock user model for response
        user_model = Mock()
        user_model.name = "Test User"
        user_model.email = "test@example.com"
        user_model.avatar_url = None
        user_result = MagicMock()
        user_result.scalar_one.return_value = user_model

        # Set up session.execute to return different results based on query
        execute_calls = []

        async def mock_execute(query):
            query_str = str(query).upper()
            execute_calls.append(query_str)
            # First call: check existing member (OrganizationMemberModel)
            if len(execute_calls) == 1:
                return mock_result
            # Second call: get user details (UserModel)
            elif len(execute_calls) == 2 and ("USER" in query_str or "USERS" in query_str):
                return user_result
            else:
                return mock_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Mock refresh to set created_at after flush
        async def mock_refresh(obj):
            if hasattr(obj, "user_id"):
                obj.created_at = datetime.utcnow()

        mock_session.refresh = AsyncMock(side_effect=mock_refresh)

        use_case = AddOrganizationMemberUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        result = await use_case.execute(str(test_organization.id), request)

        assert result.user_id == test_user.id
        assert result.role == "member"
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_member_organization_not_found(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test add member fails when organization not found."""
        request = AddMemberRequest(user_id=test_user.id)
        mock_organization_repository.get_by_id.return_value = None

        use_case = AddOrganizationMemberUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)

        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_member_user_not_found(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
    ):
        """Test add member fails when user not found."""
        request = AddMemberRequest(user_id=uuid4())
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = None

        use_case = AddOrganizationMemberUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(test_organization.id), request)

    @pytest.mark.asyncio
    async def test_add_member_already_member(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test add member fails when user is already a member."""
        request = AddMemberRequest(user_id=test_user.id)
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        # Mock existing member
        existing_member = Mock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_member
        mock_session.execute = AsyncMock(return_value=mock_result)

        use_case = AddOrganizationMemberUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ConflictException):
            await use_case.execute(str(test_organization.id), request)

        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_member_invalid_role(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test add member fails with invalid role."""
        request = AddMemberRequest(user_id=test_user.id, role="invalid_role")
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        use_case = AddOrganizationMemberUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ValidationException):
            await use_case.execute(str(test_organization.id), request)


class TestListOrganizationMembersUseCase:
    """Tests for ListOrganizationMembersUseCase."""

    @pytest.mark.asyncio
    async def test_list_members_success(
        self, mock_organization_repository, mock_session, test_organization
    ):
        """Test successful member listing."""
        mock_organization_repository.get_by_id.return_value = test_organization

        # Mock count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        # Mock members query
        member1 = Mock()
        member1.user_id = uuid4()
        member1.organization_id = test_organization.id
        member1.role = "admin"
        member1.created_at = datetime.utcnow()

        member2 = Mock()
        member2.user_id = uuid4()
        member2.organization_id = test_organization.id
        member2.role = "member"
        member2.created_at = datetime.utcnow()

        user1 = Mock()
        user1.name = "User 1"
        user1.email = "user1@example.com"
        user1.avatar_url = None

        user2 = Mock()
        user2.name = "User 2"
        user2.email = "user2@example.com"
        user2.avatar_url = None

        members_result = MagicMock()
        members_result.all.return_value = [(member1, user1), (member2, user2)]

        mock_session.execute = AsyncMock(side_effect=[count_result, members_result])

        use_case = ListOrganizationMembersUseCase(mock_organization_repository, mock_session)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20)

        assert len(result.members) == 2
        assert result.total == 2
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_list_members_organization_not_found(
        self, mock_organization_repository, mock_session
    ):
        """Test list members fails when organization not found."""
        mock_organization_repository.get_by_id.return_value = None

        use_case = ListOrganizationMembersUseCase(mock_organization_repository, mock_session)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), page=1, limit=20)


class TestUpdateOrganizationMemberRoleUseCase:
    """Tests for UpdateOrganizationMemberRoleUseCase."""

    @pytest.mark.asyncio
    async def test_update_role_success(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test successful role update."""
        request = UpdateMemberRoleRequest(role="admin")
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        # Mock member
        org_member = Mock()
        org_member.role = "member"
        org_member.user_id = test_user.id
        org_member.organization_id = test_organization.id
        org_member.created_at = datetime.utcnow()

        member_result = MagicMock()
        member_result.scalar_one_or_none.return_value = org_member

        # Mock admin count (more than 1, so safe to change)
        admin_count_result = MagicMock()
        admin_count_result.scalar_one.return_value = 2

        # Mock user model
        user_model = Mock()
        user_model.name = "Test User"
        user_model.email = "test@example.com"
        user_model.avatar_url = None
        user_result = MagicMock()
        user_result.scalar_one.return_value = user_model

        # Note: When updating FROM member TO admin, admin_count check is skipped
        # because old_role != Role.ADMIN.value, so only 2 execute calls:
        # 1. Get member, 2. Get user model
        mock_session.execute = AsyncMock(side_effect=[member_result, user_result])

        # Mock refresh
        mock_session.refresh = AsyncMock()

        use_case = UpdateOrganizationMemberRoleUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        result = await use_case.execute(
            str(test_organization.id),
            str(test_user.id),
            request,
            str(uuid4()),
        )

        assert result.role == "admin"
        assert org_member.role == "admin"

    @pytest.mark.asyncio
    async def test_update_role_prevent_remove_last_admin(
        self,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test update role prevents removing last admin."""
        request = UpdateMemberRoleRequest(role="member")
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        # Mock member (currently admin)
        org_member = Mock()
        org_member.role = Role.ADMIN.value
        org_member.user_id = test_user.id
        org_member.organization_id = test_organization.id

        member_result = MagicMock()
        member_result.scalar_one_or_none.return_value = org_member

        # Mock admin count (only 1 admin - last one)
        admin_count_result = MagicMock()
        admin_count_result.scalar_one.return_value = 1

        mock_session.execute = AsyncMock(side_effect=[member_result, admin_count_result])

        use_case = UpdateOrganizationMemberRoleUseCase(
            mock_organization_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(
                str(test_organization.id),
                str(test_user.id),
                request,
                str(uuid4()),
            )

        assert "last admin" in str(exc_info.value).lower()


class TestRemoveOrganizationMemberUseCase:
    """Tests for RemoveOrganizationMemberUseCase."""

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self, mock_organization_repository, mock_session, test_organization
    ):
        """Test successful member removal."""
        mock_organization_repository.get_by_id.return_value = test_organization

        # Mock member (non-admin)
        org_member = Mock()
        org_member.role = "member"
        org_member.user_id = uuid4()
        org_member.organization_id = test_organization.id

        member_result = MagicMock()
        member_result.scalar_one_or_none.return_value = org_member

        mock_session.execute = AsyncMock(return_value=member_result)

        use_case = RemoveOrganizationMemberUseCase(mock_organization_repository, mock_session)

        await use_case.execute(str(test_organization.id), str(uuid4()), str(uuid4()))

        mock_session.delete.assert_called_once_with(org_member)

    @pytest.mark.asyncio
    async def test_remove_member_prevent_remove_last_admin(
        self, mock_organization_repository, mock_session, test_organization
    ):
        """Test remove member prevents removing last admin."""
        mock_organization_repository.get_by_id.return_value = test_organization

        # Mock member (admin)
        org_member = Mock()
        org_member.role = Role.ADMIN.value
        org_member.user_id = uuid4()
        org_member.organization_id = test_organization.id

        member_result = MagicMock()
        member_result.scalar_one_or_none.return_value = org_member

        # Mock admin count (only 1 admin - last one)
        admin_count_result = MagicMock()
        admin_count_result.scalar_one.return_value = 1

        mock_session.execute = AsyncMock(side_effect=[member_result, admin_count_result])

        use_case = RemoveOrganizationMemberUseCase(mock_organization_repository, mock_session)

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(test_organization.id), str(uuid4()), str(uuid4()))

        assert "last admin" in str(exc_info.value).lower()
        mock_session.delete.assert_not_called()
