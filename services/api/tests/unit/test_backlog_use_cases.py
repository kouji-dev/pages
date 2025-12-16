"""Unit tests for backlog use cases."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.dtos.backlog import (
    PrioritizeBacklogRequest,
    ReorderBacklogIssueRequest,
)
from src.application.use_cases.backlog import (
    ListBacklogUseCase,
    PrioritizeBacklogUseCase,
    ReorderBacklogIssueUseCase,
)
from src.domain.entities import Project
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def mock_sprint_repository():
    """Mock sprint repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
        description="A test project",
    )


class TestListBacklogUseCase:
    """Tests for ListBacklogUseCase."""

    @pytest.mark.asyncio
    async def test_list_backlog_success(
        self,
        mock_issue_repository,
        mock_sprint_repository,
        mock_project_repository,
        mock_session,
        test_project,
    ):
        """Test successful backlog listing."""
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        mock_project_repository.get_by_id.return_value = test_project

        # Mock sprint issues (empty - all issues in backlog)
        mock_sprint_result = MagicMock()
        mock_sprint_result.all.return_value = []
        mock_session.execute.return_value = mock_sprint_result

        # Mock backlog issues
        issue1 = MagicMock(spec=IssueModel)
        issue1.id = uuid4()
        issue2 = MagicMock(spec=IssueModel)
        issue2.id = uuid4()

        mock_issues_result = MagicMock()
        mock_issues_result.scalars.return_value.all.return_value = [issue1, issue2]
        mock_session.execute.side_effect = [
            mock_sprint_result,  # First call for sprint issues
            MagicMock(scalar_one=MagicMock(return_value=2)),  # Count query
            mock_issues_result,  # Issues query
        ]

        use_case = ListBacklogUseCase(
            mock_issue_repository,
            mock_sprint_repository,
            mock_project_repository,
            mock_session,
        )
        result = await use_case.execute(test_project.id)

        assert result.total == 2
        assert len(result.issues) == 2
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_backlog_with_filters(
        self,
        mock_issue_repository,
        mock_sprint_repository,
        mock_project_repository,
        mock_session,
        test_project,
    ):
        """Test backlog listing with filters."""
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        mock_project_repository.get_by_id.return_value = test_project

        # Mock empty sprint issues
        mock_sprint_result = MagicMock()
        mock_sprint_result.all.return_value = []

        # Mock count result
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        # Mock issues result (empty)
        mock_issues_result = MagicMock()
        mock_issues_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [
            mock_sprint_result,  # First call for sprint issues
            mock_count_result,  # Count query
            mock_issues_result,  # Issues query
        ]

        use_case = ListBacklogUseCase(
            mock_issue_repository,
            mock_sprint_repository,
            mock_project_repository,
            mock_session,
        )
        result = await use_case.execute(
            test_project.id,
            page=1,
            limit=10,
            type_filter="task",
            priority_filter="high",
        )

        assert result.page == 1
        assert result.limit == 10
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_backlog_project_not_found(
        self,
        mock_issue_repository,
        mock_sprint_repository,
        mock_project_repository,
        mock_session,
    ):
        """Test backlog listing when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = ListBacklogUseCase(
            mock_issue_repository,
            mock_sprint_repository,
            mock_project_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4())


class TestPrioritizeBacklogUseCase:
    """Tests for PrioritizeBacklogUseCase."""

    @pytest.mark.asyncio
    async def test_prioritize_backlog_success(
        self,
        mock_project_repository,
        mock_session,
        test_project,
    ):
        """Test successful backlog prioritization."""
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        mock_project_repository.get_by_id.return_value = test_project

        issue1 = MagicMock(spec=IssueModel)
        issue1.id = uuid4()
        issue1.backlog_order = None

        issue2 = MagicMock(spec=IssueModel)
        issue2.id = uuid4()
        issue2.backlog_order = None

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = issue1

        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = issue2

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        request = PrioritizeBacklogRequest(issue_ids=[issue1.id, issue2.id])

        use_case = PrioritizeBacklogUseCase(mock_project_repository, mock_session)
        await use_case.execute(test_project.id, request)

        assert issue1.backlog_order == 0
        assert issue2.backlog_order == 1
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_prioritize_backlog_project_not_found(
        self,
        mock_project_repository,
        mock_session,
    ):
        """Test prioritization when project not found."""
        mock_project_repository.get_by_id.return_value = None

        request = PrioritizeBacklogRequest(issue_ids=[uuid4()])

        use_case = PrioritizeBacklogUseCase(mock_project_repository, mock_session)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), request)


class TestReorderBacklogIssueUseCase:
    """Tests for ReorderBacklogIssueUseCase."""

    @pytest.mark.asyncio
    async def test_reorder_backlog_issue_success(
        self,
        mock_project_repository,
        mock_sprint_repository,
        mock_session,
        test_project,
    ):
        """Test successful backlog issue reordering."""
        from datetime import datetime
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        mock_project_repository.get_by_id.return_value = test_project

        issue = MagicMock(spec=IssueModel)
        issue.id = uuid4()
        issue.backlog_order = 1
        issue.created_at = datetime.utcnow()

        # Mock: issue exists
        mock_issue_result = MagicMock()
        mock_issue_result.scalar_one_or_none.return_value = issue

        # Mock: issue not in any sprint
        mock_sprint_repository.get_issue_sprint.return_value = None

        # Mock: get all backlog issues (empty sprint issues list)
        mock_sprint_issues_result = MagicMock()
        mock_sprint_issues_result.all.return_value = []

        # Mock: get backlog issues
        mock_backlog_result = MagicMock()
        mock_backlog_result.scalars.return_value.all.return_value = []

        mock_session.execute.side_effect = [
            mock_issue_result,  # Get issue
            mock_sprint_issues_result,  # Get sprint issues
            mock_backlog_result,  # Get backlog issues
        ]

        request = ReorderBacklogIssueRequest(position=0)

        use_case = ReorderBacklogIssueUseCase(
            mock_project_repository, mock_sprint_repository, mock_session
        )
        await use_case.execute(test_project.id, issue.id, request)

        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_reorder_backlog_issue_project_not_found(
        self,
        mock_project_repository,
        mock_sprint_repository,
        mock_session,
    ):
        """Test reordering when project not found."""
        mock_project_repository.get_by_id.return_value = None

        request = ReorderBacklogIssueRequest(position=0)

        use_case = ReorderBacklogIssueUseCase(
            mock_project_repository, mock_sprint_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), uuid4(), request)
