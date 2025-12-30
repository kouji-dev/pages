"""Unit tests for project use cases."""

from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.project import CreateProjectRequest, UpdateProjectRequest
from src.application.use_cases.project import (
    CreateProjectUseCase,
    DeleteProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)
from src.domain.entities import Organization, Project, User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
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
def test_project(test_organization):
    """Create a test project."""
    return Project.create(
        organization_id=test_organization.id,
        name="Test Project",
        key="TEST",
        description="A test project",
    )


class TestCreateProjectUseCase:
    """Tests for CreateProjectUseCase."""

    @pytest.mark.asyncio
    async def test_create_project_success(
        self,
        mock_project_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test successful project creation."""
        # Setup mocks
        request = CreateProjectRequest(
            organization_id=test_organization.id,
            name="New Project",
            key="NEW",
            description="Description",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization

        created_project = Project.create(
            organization_id=request.organization_id,
            name=request.name,
            key=request.key,
            description=request.description,
        )
        mock_project_repository.create.return_value = created_project
        mock_project_repository.exists_by_key.return_value = False

        # Mock ProjectMemberModel add
        mock_session.add = Mock()
        mock_session.flush = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreateProjectUseCase(
            mock_project_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Execute
        result = await use_case.execute(request, str(test_user.id))

        # Assert
        assert result.name == "New Project"
        assert result.key == "NEW"
        assert result.description == "Description"
        assert result.organization_id == test_organization.id
        mock_project_repository.create.assert_called_once()
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_auto_key(
        self,
        mock_project_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test project creation with auto-generated key."""
        request = CreateProjectRequest(
            organization_id=test_organization.id,
            name="My Awesome Project",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization

        created_project = Project.create(
            organization_id=request.organization_id,
            name=request.name,
        )
        mock_project_repository.create.return_value = created_project
        mock_project_repository.exists_by_key.return_value = False

        mock_session.add = Mock()
        mock_session.flush = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = CreateProjectUseCase(
            mock_project_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.name == "My Awesome Project"
        assert result.key == "MYAWESOMEP"  # Auto-generated from name (max 10 chars)
        mock_project_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_organization_not_found(
        self,
        mock_project_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test project creation fails when organization not found."""
        request = CreateProjectRequest(
            organization_id=uuid4(),
            name="New Project",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = None

        use_case = CreateProjectUseCase(
            mock_project_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="Organization"):
            await use_case.execute(request, str(test_user.id))

    @pytest.mark.asyncio
    async def test_create_project_user_not_found(
        self,
        mock_project_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
    ):
        """Test project creation fails when user not found."""
        request = CreateProjectRequest(
            organization_id=test_organization.id,
            name="New Project",
        )
        mock_user_repository.get_by_id.return_value = None
        mock_organization_repository.get_by_id.return_value = test_organization

        use_case = CreateProjectUseCase(
            mock_project_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(request, str(uuid4()))

    @pytest.mark.asyncio
    async def test_create_project_key_conflict(
        self,
        mock_project_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_user,
        test_organization,
    ):
        """Test project creation fails with duplicate key in organization."""
        request = CreateProjectRequest(
            organization_id=test_organization.id,
            name="New Project",
            key="TEST",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization
        # Mock that key already exists, so create will raise ConflictException
        mock_project_repository.create.side_effect = ConflictException(
            "Project with key 'TEST' already exists in this organization", field="key"
        )

        use_case = CreateProjectUseCase(
            mock_project_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        with pytest.raises(ConflictException, match="key"):
            await use_case.execute(request, str(test_user.id))


class TestGetProjectUseCase:
    """Tests for GetProjectUseCase."""

    @pytest.mark.asyncio
    async def test_get_project_success(self, mock_project_repository, mock_session, test_project):
        """Test successful project retrieval."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = GetProjectUseCase(mock_project_repository, mock_session)

        result = await use_case.execute(str(test_project.id))

        assert result.id == test_project.id
        assert result.name == test_project.name
        assert result.key == test_project.key
        mock_project_repository.get_by_id.assert_called_once_with(test_project.id)

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, mock_project_repository, mock_session):
        """Test project retrieval fails when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = GetProjectUseCase(mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()))


class TestListProjectsUseCase:
    """Tests for ListProjectsUseCase."""

    @pytest.mark.asyncio
    async def test_list_projects_success(
        self, mock_project_repository, mock_session, test_organization, test_project
    ):
        """Test successful project listing."""

        projects = [test_project]
        mock_project_repository.get_all.return_value = projects
        mock_project_repository.count.return_value = 1

        # Mock execute calls sequence:
        # 1. Count members
        # 2. Count issues
        # 3. Count completed issues
        # 4. Get top 5 members (returns empty list)
        call_count = [0]

        async def mock_execute(query):
            call_count[0] += 1
            query_str = str(query).upper()

            # Count queries (members, issues, completed issues)
            if "COUNT" in query_str:
                result = MagicMock()
                result.scalar_one.return_value = 0
                return result

            # Members query (join ProjectMemberModel and UserModel)
            elif "PROJECTMEMBER" in query_str and "USER" in query_str:
                result = MagicMock()
                result.all.return_value = []  # Empty members list
                return result

            # Default
            result = MagicMock()
            result.scalar_one.return_value = 0
            return result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        use_case = ListProjectsUseCase(mock_project_repository, mock_session)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20, search=None)

        assert len(result.projects) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.limit == 20
        assert result.pages == 1
        # Check new fields
        project = result.projects[0]
        assert project.deleted_at is None or project.deleted_at == test_project.deleted_at
        assert project.completed_issues_count == 0
        assert project.members == []
        mock_project_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_projects_with_search(
        self, mock_project_repository, mock_session, test_organization, test_project
    ):
        """Test project listing with search query."""
        projects = [test_project]
        mock_project_repository.search.return_value = projects
        mock_project_repository.count.return_value = 1

        # Mock execute calls sequence
        call_count = [0]

        async def mock_execute(query):
            call_count[0] += 1
            query_str = str(query).upper()

            # Count queries
            if "COUNT" in query_str:
                result = MagicMock()
                result.scalar_one.return_value = 0
                return result

            # Members query
            elif "PROJECTMEMBER" in query_str and "USER" in query_str:
                result = MagicMock()
                result.all.return_value = []
                return result

            result = MagicMock()
            result.scalar_one.return_value = 0
            return result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        use_case = ListProjectsUseCase(mock_project_repository, mock_session)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20, search="Test")

        assert len(result.projects) == 1
        mock_project_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_projects_with_members_and_issues(
        self, mock_project_repository, mock_session, test_organization, test_project
    ):
        """Test project listing with members and completed issues."""
        from datetime import datetime

        projects = [test_project]
        mock_project_repository.get_all.return_value = projects
        mock_project_repository.count.return_value = 1

        # Create mock member and user
        member = MagicMock()
        member.user_id = uuid4()
        member.project_id = test_project.id
        member.role = "admin"
        member.created_at = datetime.utcnow()

        user = MagicMock()
        user.name = "Test User"
        user.email = "test@example.com"
        user.avatar_url = None

        call_count = [0]

        async def mock_execute(query):
            call_count[0] += 1

            # Count members
            if call_count[0] == 1:
                result = MagicMock()
                result.scalar_one.return_value = 1
                return result

            # Count issues
            elif call_count[0] == 2:
                result = MagicMock()
                result.scalar_one.return_value = 10
                return result

            # Count completed issues
            elif call_count[0] == 3:
                result = MagicMock()
                result.scalar_one.return_value = 5
                return result

            # Get members
            elif call_count[0] == 4:
                result = MagicMock()
                result.all.return_value = [(member, user)]
                return result

            result = MagicMock()
            result.scalar_one.return_value = 0
            return result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        use_case = ListProjectsUseCase(mock_project_repository, mock_session)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20, search=None)

        assert len(result.projects) == 1
        project = result.projects[0]
        assert project.member_count == 1
        assert project.issue_count == 10
        assert project.completed_issues_count == 5
        assert len(project.members) == 1
        assert project.members[0].user_name == "Test User"
        assert project.members[0].role == "admin"


class TestUpdateProjectUseCase:
    """Tests for UpdateProjectUseCase."""

    @pytest.mark.asyncio
    async def test_update_project_success(
        self, mock_project_repository, mock_session, test_project
    ):
        """Test successful project update."""
        mock_project_repository.get_by_id.return_value = test_project

        updated_project = Project(
            id=test_project.id,
            organization_id=test_project.organization_id,
            name="Updated Project",
            key=test_project.key,
            description="Updated description",
        )
        mock_project_repository.update.return_value = updated_project
        mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one=Mock(return_value=0)))

        use_case = UpdateProjectUseCase(mock_project_repository, mock_session)

        request = UpdateProjectRequest(name="Updated Project", description="Updated description")
        result = await use_case.execute(str(test_project.id), request)

        assert result.name == "Updated Project"
        assert result.description == "Updated description"
        mock_project_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, mock_project_repository, mock_session):
        """Test project update fails when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = UpdateProjectUseCase(mock_project_repository, mock_session)

        request = UpdateProjectRequest(name="Updated Project")
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_update_project_key_conflict(
        self, mock_project_repository, mock_session, test_project
    ):
        """Test project update fails with duplicate key."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_project_repository.update.side_effect = ConflictException(
            "Project with key 'CONFLICT' already exists", field="key"
        )

        use_case = UpdateProjectUseCase(mock_project_repository, mock_session)

        request = UpdateProjectRequest(key="CONFLICT")
        with pytest.raises(ConflictException, match="key"):
            await use_case.execute(str(test_project.id), request)


class TestDeleteProjectUseCase:
    """Tests for DeleteProjectUseCase."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, mock_project_repository, test_project):
        """Test successful project deletion (soft delete)."""
        mock_project_repository.get_by_id.return_value = test_project

        # After delete, project should have deleted_at set
        deleted_project = Project(
            id=test_project.id,
            organization_id=test_project.organization_id,
            name=test_project.name,
            key=test_project.key,
        )
        deleted_project.delete()
        mock_project_repository.update.return_value = deleted_project

        use_case = DeleteProjectUseCase(mock_project_repository)

        await use_case.execute(str(test_project.id))

        mock_project_repository.get_by_id.assert_called_once_with(test_project.id)
        mock_project_repository.update.assert_called_once()
        # Verify soft delete was called
        assert mock_project_repository.update.call_args[0][0].deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, mock_project_repository):
        """Test project deletion fails when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = DeleteProjectUseCase(mock_project_repository)

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()))
