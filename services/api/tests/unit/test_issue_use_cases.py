"""Unit tests for issue use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.issue import CreateIssueRequest, UpdateIssueRequest
from src.application.use_cases.issue import (
    CreateIssueUseCase,
    DeleteIssueUseCase,
    GetIssueUseCase,
    ListIssuesUseCase,
    UpdateIssueUseCase,
)
from src.domain.entities import Issue, Project, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


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
def mock_activity_repository():
    """Mock issue activity repository."""
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


@pytest.fixture
def test_issue(test_project, test_user):
    """Create a test issue."""
    return Issue.create(
        project_id=test_project.id,
        issue_number=1,
        title="Test Issue",
        description="A test issue",
        type="task",
        status="todo",
        priority="medium",
        reporter_id=test_user.id,
    )


class TestCreateIssueUseCase:
    """Tests for CreateIssueUseCase."""

    @pytest.mark.asyncio
    async def test_create_issue_success(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_activity_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test successful issue creation."""
        request = CreateIssueRequest(
            project_id=test_project.id,
            title="New Issue",
            description="Description",
            type="bug",
            status="todo",
            priority="high",
        )
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = test_user
        mock_issue_repository.get_next_issue_number.return_value = 1

        created_issue = Issue.create(
            project_id=request.project_id,
            issue_number=1,
            title=request.title,
            description=request.description,
            type=request.type,
            status=request.status,
            priority=request.priority,
            reporter_id=test_user.id,
        )
        mock_issue_repository.create.return_value = created_issue

        use_case = CreateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.title == "New Issue"
        assert result.type == "bug"
        assert result.status == "todo"
        assert result.priority == "high"
        assert result.key == "TEST-1"  # Generated key
        assert result.issue_number == 1
        mock_issue_repository.get_next_issue_number.assert_called_once()
        mock_issue_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issue_project_not_found(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_user,
    ):
        """Test issue creation fails when project not found."""
        request = CreateIssueRequest(
            project_id=uuid4(),
            title="New Issue",
        )
        mock_project_repository.get_by_id.return_value = None

        use_case = CreateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(request, str(test_user.id))

    @pytest.mark.asyncio
    async def test_create_issue_reporter_not_found(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
    ):
        """Test issue creation fails when reporter not found."""
        request = CreateIssueRequest(
            project_id=test_project.id,
            title="New Issue",
        )
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.return_value = None

        use_case = CreateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(request, str(uuid4()))

    @pytest.mark.asyncio
    async def test_create_issue_assignee_not_found(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_project,
        test_user,
    ):
        """Test issue creation fails when assignee not found."""
        request = CreateIssueRequest(
            project_id=test_project.id,
            title="New Issue",
            assignee_id=uuid4(),
        )
        mock_project_repository.get_by_id.return_value = test_project
        mock_user_repository.get_by_id.side_effect = [test_user, None]

        use_case = CreateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException, match="User"):
            await use_case.execute(request, str(test_user.id))


class TestGetIssueUseCase:
    """Tests for GetIssueUseCase."""

    @pytest.mark.asyncio
    async def test_get_issue_success(
        self, mock_issue_repository, mock_project_repository, mock_session, test_issue, test_project
    ):
        """Test successful issue retrieval."""
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_project_repository.get_by_id.return_value = test_project

        use_case = GetIssueUseCase(mock_issue_repository, mock_project_repository, mock_session)

        result = await use_case.execute(str(test_issue.id))

        assert result.id == test_issue.id
        assert result.title == test_issue.title
        assert result.key == "TEST-1"  # Generated key
        mock_issue_repository.get_by_id.assert_called_once_with(test_issue.id)

    @pytest.mark.asyncio
    async def test_get_issue_not_found(
        self, mock_issue_repository, mock_project_repository, mock_session
    ):
        """Test issue retrieval fails when issue not found."""
        mock_issue_repository.get_by_id.return_value = None

        use_case = GetIssueUseCase(mock_issue_repository, mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(str(uuid4()))


class TestListIssuesUseCase:
    """Tests for ListIssuesUseCase."""

    @pytest.mark.asyncio
    async def test_list_issues_success(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
        test_project,
        test_issue,
    ):
        """Test successful issue listing."""
        issues = [test_issue]
        mock_issue_repository.get_all.return_value = issues
        mock_issue_repository.count.return_value = 1
        mock_project_repository.get_by_id.return_value = test_project

        use_case = ListIssuesUseCase(mock_issue_repository, mock_project_repository, mock_session)

        result = await use_case.execute(str(test_project.id), page=1, limit=20, search=None)

        assert len(result.issues) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.limit == 20
        assert result.pages == 1
        assert result.issues[0].key == "TEST-1"  # Generated key
        mock_issue_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_issues_with_filters(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
        test_project,
        test_issue,
    ):
        """Test issue listing with filters."""
        issues = [test_issue]
        mock_issue_repository.get_all.return_value = issues
        mock_issue_repository.count.return_value = 1
        mock_project_repository.get_by_id.return_value = test_project

        use_case = ListIssuesUseCase(mock_issue_repository, mock_project_repository, mock_session)

        result = await use_case.execute(
            str(test_project.id),
            page=1,
            limit=20,
            status="todo",
            type="task",
            priority="medium",
        )

        assert len(result.issues) == 1
        mock_issue_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_issues_with_search(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
        test_project,
        test_issue,
    ):
        """Test issue listing with search query."""
        issues = [test_issue]
        mock_issue_repository.search.return_value = issues
        mock_issue_repository.count.return_value = 1
        mock_project_repository.get_by_id.return_value = test_project

        use_case = ListIssuesUseCase(mock_issue_repository, mock_project_repository, mock_session)

        result = await use_case.execute(str(test_project.id), page=1, limit=20, search="Test")

        assert len(result.issues) == 1
        mock_issue_repository.search.assert_called_once()


class TestUpdateIssueUseCase:
    """Tests for UpdateIssueUseCase."""

    @pytest.mark.asyncio
    async def test_update_issue_success(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_activity_repository,
        mock_session,
        test_issue,
        test_project,
        test_user,
    ):
        """Test successful issue update."""
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_project_repository.get_by_id.return_value = test_project

        updated_issue = Issue(
            id=test_issue.id,
            project_id=test_issue.project_id,
            issue_number=test_issue.issue_number,
            title="Updated Issue",
            description="Updated description",
            type=test_issue.type,
            status="in_progress",
            priority=test_issue.priority,
            reporter_id=test_issue.reporter_id,
        )
        mock_issue_repository.update.return_value = updated_issue

        use_case = UpdateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        request = UpdateIssueRequest(
            title="Updated Issue", description="Updated description", status="in_progress"
        )
        result = await use_case.execute(str(test_issue.id), request, test_user.id)

        assert result.title == "Updated Issue"
        assert result.description == "Updated description"
        assert result.status == "in_progress"
        assert result.key == "TEST-1"  # Generated key
        mock_issue_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_issue_not_found(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_activity_repository,
        mock_session,
    ):
        """Test issue update fails when issue not found."""
        mock_issue_repository.get_by_id.return_value = None

        use_case = UpdateIssueUseCase(
            mock_issue_repository,
            mock_project_repository,
            mock_user_repository,
            mock_activity_repository,
            mock_session,
        )

        request = UpdateIssueRequest(title="Updated Issue")
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(str(uuid4()), request, uuid4())

    @pytest.mark.asyncio
    async def test_update_issue_invalid_status(
        self,
        mock_issue_repository,
        mock_project_repository,
        mock_user_repository,
        mock_session,
        test_issue,
        test_project,
    ):
        """Test issue update fails with invalid status."""
        from pydantic import ValidationError

        # The validation happens at the DTO level, not in the use case
        with pytest.raises(ValidationError):
            UpdateIssueRequest(status="invalid_status")


class TestDeleteIssueUseCase:
    """Tests for DeleteIssueUseCase."""

    @pytest.mark.asyncio
    async def test_delete_issue_success(
        self, mock_issue_repository, mock_activity_repository, test_issue
    ):
        """Test successful issue deletion (soft delete)."""
        mock_issue_repository.get_by_id.return_value = test_issue

        # After delete, issue should have deleted_at set
        deleted_issue = Issue(
            id=test_issue.id,
            project_id=test_issue.project_id,
            issue_number=test_issue.issue_number,
            title=test_issue.title,
        )
        deleted_issue.delete()
        mock_issue_repository.update.return_value = deleted_issue

        use_case = DeleteIssueUseCase(mock_issue_repository, mock_activity_repository)

        await use_case.execute(str(test_issue.id))

        mock_issue_repository.get_by_id.assert_called_once_with(test_issue.id)
        mock_issue_repository.update.assert_called_once()
        # Verify soft delete was called
        assert mock_issue_repository.update.call_args[0][0].deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_issue_not_found(self, mock_issue_repository, mock_activity_repository):
        """Test issue deletion fails when issue not found."""
        mock_issue_repository.get_by_id.return_value = None

        use_case = DeleteIssueUseCase(mock_issue_repository, mock_activity_repository)

        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(str(uuid4()))
