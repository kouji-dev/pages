"""Unit tests for project member use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.project_member import (
    AddProjectMemberRequest,
    UpdateProjectMemberRoleRequest,
)
from src.application.use_cases.project.project_member import (
    AddProjectMemberUseCase,
    ListProjectMembersUseCase,
    RemoveProjectMemberUseCase,
    UpdateProjectMemberRoleUseCase,
)
from src.domain.entities import Project, User
from src.domain.exceptions import ConflictException, EntityNotFoundException, ValidationException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
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
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
        description="A test project",
    )


class TestAddProjectMemberUseCase:
    """Tests for AddProjectMemberUseCase."""

    @pytest.mark.asyncio
    async def test_add_project_member_success(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test successful project member addition."""

        request = AddProjectMemberRequest(user_id=test_user.id, role="member")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        # Mock existing member check (should return None)
        # Mock user model for response
        user_model = Mock()
        user_model.id = test_user.id
        user_model.name = "Test User"
        user_model.email = "test@example.com"
        user_model.avatar_url = None

        execute_calls = []

        async def mock_execute(query):
            query_str = str(query).upper()
            execute_calls.append(query_str)
            # First call: check existing member (ProjectMemberModel)
            if len(execute_calls) == 1:
                result = MagicMock()
                result.scalar_one_or_none.return_value = None
                return result
            # Second call: get user details (UserModel)
            elif len(execute_calls) == 2 and ("USER" in query_str or "USERS" in query_str):
                result = MagicMock()
                result.scalar_one.return_value = user_model
                return result
            else:
                result = MagicMock()
                result.scalar_one_or_none.return_value = None
                return result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Mock refresh to set created_at after flush
        async def mock_refresh(obj):
            if hasattr(obj, "user_id"):
                obj.created_at = datetime.utcnow()

        mock_session.refresh = AsyncMock(side_effect=mock_refresh)

        use_case = AddProjectMemberUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        result = await use_case.execute(str(test_project.id), request)

        assert result.user_id == test_user.id
        assert result.project_id == test_project.id
        assert result.role == "member"
        assert result.user_name == "Test User"
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_project_member_project_not_found(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test add member fails when project not found."""
        request = AddProjectMemberRequest(user_id=test_user.id, role="member")
        mock_project_repository.get_by_id.return_value = None

        use_case = AddProjectMemberUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_add_project_member_user_not_found(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
    ):
        """Test add member fails when user not found."""
        request = AddProjectMemberRequest(user_id=uuid4(), role="member")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = None

        use_case = AddProjectMemberUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(str(test_project.id), request)

    @pytest.mark.asyncio
    async def test_add_project_member_invalid_role(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test add member fails with invalid role."""
        request = AddProjectMemberRequest(user_id=test_user.id, role="invalid_role")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        use_case = AddProjectMemberUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ValidationException, match="Invalid role"):
            await use_case.execute(str(test_project.id), request)

    @pytest.mark.asyncio
    async def test_add_project_member_already_member(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test add member fails when user is already a member."""

        request = AddProjectMemberRequest(user_id=test_user.id, role="member")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        # Mock existing member (should return a member)
        existing_member = Mock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_member
        mock_session.execute.return_value = mock_result

        use_case = AddProjectMemberUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ConflictException, match="already a member"):
            await use_case.execute(str(test_project.id), request)


class TestListProjectMembersUseCase:
    """Tests for ListProjectMembersUseCase."""

    @pytest.mark.asyncio
    async def test_list_project_members_success(
        self, mock_project_repository, mock_session, test_project
    ):
        """Test successful project member listing."""

        mock_project_repository.get_by_id.return_value = test_project

        # Mock count result
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        # Mock members result
        member1 = MagicMock()
        member1.user_id = uuid4()
        member1.project_id = test_project.id
        member1.role = "admin"
        member1.created_at = datetime.utcnow()

        member2 = MagicMock()
        member2.user_id = uuid4()
        member2.project_id = test_project.id
        member2.role = "member"
        member2.created_at = datetime.utcnow()

        user1 = MagicMock()
        user1.name = "User 1"
        user1.email = "user1@example.com"
        user1.avatar_url = None

        user2 = MagicMock()
        user2.name = "User 2"
        user2.email = "user2@example.com"
        user2.avatar_url = None

        # Mock execute calls
        async def execute_side_effect(query):
            if "count" in str(query):
                return count_result
            else:
                result = MagicMock()
                result.all.return_value = [
                    (member1, user1),
                    (member2, user2),
                ]
                return result

        mock_session.execute.side_effect = execute_side_effect

        use_case = ListProjectMembersUseCase(mock_project_repository, mock_session)

        result = await use_case.execute(str(test_project.id), page=1, limit=20)

        assert len(result.members) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_project_members_project_not_found(
        self, mock_project_repository, mock_session
    ):
        """Test list members fails when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = ListProjectMembersUseCase(mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), page=1, limit=20)


class TestUpdateProjectMemberRoleUseCase:
    """Tests for UpdateProjectMemberRoleUseCase."""

    @pytest.mark.asyncio
    async def test_update_project_member_role_success(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test successful project member role update."""

        request = UpdateProjectMemberRoleRequest(role="admin")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        # Mock existing member
        project_member = Mock()
        project_member.user_id = test_user.id
        project_member.project_id = test_project.id
        project_member.role = "member"
        project_member.created_at = datetime.utcnow()

        # Mock user model
        user_model = Mock()
        user_model.id = test_user.id
        user_model.name = "Test User"
        user_model.email = "test@example.com"
        user_model.avatar_url = None

        # Mock execute calls
        execute_calls = []

        async def execute_side_effect(query):
            query_str = str(query).upper()
            execute_calls.append(query_str)
            result = MagicMock()
            if "PROJECTMEMBER" in query_str or "PROJECT_MEMBER" in query_str:
                result.scalar_one_or_none.return_value = project_member
            elif "USER" in query_str or "USERS" in query_str:
                result.scalar_one.return_value = user_model
            return result

        mock_session.execute = AsyncMock(side_effect=execute_side_effect)

        use_case = UpdateProjectMemberRoleUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        result = await use_case.execute(str(test_project.id), str(test_user.id), request)

        assert result.role == "admin"
        assert project_member.role == "admin"

    @pytest.mark.asyncio
    async def test_update_project_member_role_project_not_found(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test update role fails when project not found."""
        request = UpdateProjectMemberRoleRequest(role="admin")
        mock_project_repository.get_by_id.return_value = None

        use_case = UpdateProjectMemberRoleUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), str(test_user.id), request)

    @pytest.mark.asyncio
    async def test_update_project_member_role_member_not_found(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test update role fails when member not found."""
        request = UpdateProjectMemberRoleRequest(role="admin")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        # Mock no existing member
        mock_session.execute.return_value = MagicMock(scalar_one_or_none=Mock(return_value=None))

        use_case = UpdateProjectMemberRoleUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException, match="ProjectMember"):
            await use_case.execute(str(test_project.id), str(test_user.id), request)

    @pytest.mark.asyncio
    async def test_update_project_member_role_invalid_role(
        self,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test update role fails with invalid role."""
        request = UpdateProjectMemberRoleRequest(role="invalid_role")
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user

        use_case = UpdateProjectMemberRoleUseCase(
            mock_project_repository, mock_user_repository, mock_session
        )

        with pytest.raises(ValidationException, match="Invalid role"):
            await use_case.execute(str(test_project.id), str(test_user.id), request)


class TestRemoveProjectMemberUseCase:
    """Tests for RemoveProjectMemberUseCase."""

    @pytest.mark.asyncio
    async def test_remove_project_member_success(
        self, mock_project_repository, mock_session, test_project
    ):
        """Test successful project member removal."""

        mock_project_repository.get_by_id.return_value = test_project

        # Mock existing member
        user_id = uuid4()
        project_member = Mock()
        project_member.user_id = user_id
        project_member.project_id = test_project.id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = project_member
        mock_session.execute.return_value = mock_result

        use_case = RemoveProjectMemberUseCase(mock_project_repository, mock_session)

        await use_case.execute(str(test_project.id), str(user_id))

        mock_session.delete.assert_called_once_with(project_member)

    @pytest.mark.asyncio
    async def test_remove_project_member_project_not_found(
        self, mock_project_repository, mock_session
    ):
        """Test remove member fails when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = RemoveProjectMemberUseCase(mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), str(uuid4()))

    @pytest.mark.asyncio
    async def test_remove_project_member_member_not_found(
        self, mock_project_repository, mock_session, test_project
    ):
        """Test remove member fails when member not found."""

        mock_project_repository.get_by_id.return_value = test_project

        # Mock no existing member
        mock_session.execute.return_value = MagicMock(scalar_one_or_none=Mock(return_value=None))

        use_case = RemoveProjectMemberUseCase(mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="ProjectMember"):
            await use_case.execute(str(test_project.id), str(uuid4()))
