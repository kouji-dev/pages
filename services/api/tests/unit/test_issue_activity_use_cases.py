"""Unit tests for issue activity use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.issue.list_issue_activities import ListIssueActivitiesUseCase
from src.domain.entities import Issue, Project, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword
from src.infrastructure.database.models import IssueActivityModel


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def mock_activity_repository():
    """Mock issue activity repository."""
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


@pytest.fixture
def test_activity(test_issue, test_user):
    """Create a test activity."""
    activity = IssueActivityModel(
        id=uuid4(),
        issue_id=test_issue.id,
        user_id=test_user.id,
        action="created",
        field_name=None,
        old_value=None,
        new_value=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return activity


class TestListIssueActivitiesUseCase:
    """Tests for ListIssueActivitiesUseCase."""

    @pytest.mark.asyncio
    async def test_list_activities_success(
        self,
        mock_issue_repository,
        mock_activity_repository,
        mock_session,
        test_issue,
        test_user,
        test_activity,
    ):
        """Test successful listing of activities."""
        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_activity_repository.get_by_issue_id.return_value = [test_activity]
        mock_activity_repository.count_by_issue_id.return_value = 1

        # Mock user query
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [user_model]
        mock_session.execute.return_value = mock_result

        # Create use case
        use_case = ListIssueActivitiesUseCase(
            mock_issue_repository, mock_activity_repository, mock_session
        )

        # Execute
        result = await use_case.execute(str(test_issue.id), page=1, limit=50)

        # Assertions
        assert result.total == 1
        assert result.page == 1
        assert result.limit == 50
        assert result.total_pages == 1
        assert len(result.activities) == 1
        assert result.activities[0].action == "created"
        assert result.activities[0].user_id == test_user.id
        assert result.activities[0].user is not None
        assert result.activities[0].user.name == test_user.name

        # Verify calls
        mock_issue_repository.get_by_id.assert_called_once_with(test_issue.id)
        mock_activity_repository.get_by_issue_id.assert_called_once_with(
            test_issue.id, skip=0, limit=50
        )
        mock_activity_repository.count_by_issue_id.assert_called_once_with(test_issue.id)

    @pytest.mark.asyncio
    async def test_list_activities_issue_not_found(
        self,
        mock_issue_repository,
        mock_activity_repository,
        mock_session,
    ):
        """Test listing activities for non-existent issue."""
        # Setup mocks
        mock_issue_repository.get_by_id.return_value = None

        # Create use case
        use_case = ListIssueActivitiesUseCase(
            mock_issue_repository, mock_activity_repository, mock_session
        )

        # Execute and assert
        issue_id = str(uuid4())
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(issue_id)

    @pytest.mark.asyncio
    async def test_list_activities_pagination(
        self,
        mock_issue_repository,
        mock_activity_repository,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test pagination for activities."""
        # Create multiple activities
        activities = []
        for i in range(5):
            activity = IssueActivityModel(
                id=uuid4(),
                issue_id=test_issue.id,
                user_id=test_user.id,
                action="updated",
                field_name="title",
                old_value=f"Old Title {i}",
                new_value=f"New Title {i}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            activities.append(activity)

        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_activity_repository.get_by_issue_id.return_value = activities[:2]  # First page
        mock_activity_repository.count_by_issue_id.return_value = 5

        # Mock user query
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [user_model]
        mock_session.execute.return_value = mock_result

        # Create use case
        use_case = ListIssueActivitiesUseCase(
            mock_issue_repository, mock_activity_repository, mock_session
        )

        # Execute page 1
        result = await use_case.execute(str(test_issue.id), page=1, limit=2)

        # Assertions
        assert result.total == 5
        assert result.page == 1
        assert result.limit == 2
        assert result.total_pages == 3
        assert len(result.activities) == 2

        # Verify pagination
        mock_activity_repository.get_by_issue_id.assert_called_with(test_issue.id, skip=0, limit=2)

    @pytest.mark.asyncio
    async def test_list_activities_no_user(
        self,
        mock_issue_repository,
        mock_activity_repository,
        mock_session,
        test_issue,
        test_activity,
    ):
        """Test listing activities when user_id is None."""
        # Modify activity to have no user
        test_activity.user_id = None

        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_activity_repository.get_by_issue_id.return_value = [test_activity]
        mock_activity_repository.count_by_issue_id.return_value = 1

        # Mock empty user query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Create use case
        use_case = ListIssueActivitiesUseCase(
            mock_issue_repository, mock_activity_repository, mock_session
        )

        # Execute
        result = await use_case.execute(str(test_issue.id))

        # Assertions
        assert len(result.activities) == 1
        assert result.activities[0].user_id is None
        assert result.activities[0].user is None

    @pytest.mark.asyncio
    async def test_list_activities_empty(
        self,
        mock_issue_repository,
        mock_activity_repository,
        mock_session,
        test_issue,
    ):
        """Test listing activities when there are none."""
        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_activity_repository.get_by_issue_id.return_value = []
        mock_activity_repository.count_by_issue_id.return_value = 0

        # Create use case
        use_case = ListIssueActivitiesUseCase(
            mock_issue_repository, mock_activity_repository, mock_session
        )

        # Execute
        result = await use_case.execute(str(test_issue.id))

        # Assertions
        assert result.total == 0
        assert result.page == 1
        assert result.limit == 50
        assert result.total_pages == 0
        assert len(result.activities) == 0
