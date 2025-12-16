"""Unit tests for sprint use cases."""

from datetime import date
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.application.dtos.sprint import CreateSprintRequest, UpdateSprintRequest
from src.application.use_cases.sprint import (
    AddIssueToSprintUseCase,
    CompleteSprintUseCase,
    CreateSprintUseCase,
    DeleteSprintUseCase,
    GetSprintMetricsUseCase,
    GetSprintUseCase,
    ListSprintsUseCase,
    RemoveIssueFromSprintUseCase,
    ReorderSprintIssuesUseCase,
    UpdateSprintUseCase,
)
from src.domain.entities import Issue, Project, Sprint
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects.sprint_status import SprintStatus


@pytest.fixture
def mock_sprint_repository():
    """Mock sprint repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
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


@pytest.fixture
def test_sprint(test_project):
    """Create a test sprint."""
    return Sprint.create(
        project_id=test_project.id,
        name="Sprint 1",
        goal="Test goal",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 14),
        status=SprintStatus.PLANNED,
    )


class TestCreateSprintUseCase:
    """Tests for CreateSprintUseCase."""

    @pytest.mark.asyncio
    async def test_create_sprint_success(
        self,
        mock_sprint_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful sprint creation."""
        request = CreateSprintRequest(
            name="Sprint 1",
            goal="Test goal",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 14),
            status=SprintStatus.PLANNED,
        )

        mock_project_repository.get_by_id.return_value = test_project
        mock_sprint_repository.find_overlapping_sprints.return_value = []
        mock_sprint_repository.create.return_value = Sprint.create(
            project_id=test_project.id,
            name=request.name,
            goal=request.goal,
            start_date=request.start_date,
            end_date=request.end_date,
            status=request.status,
        )

        use_case = CreateSprintUseCase(mock_sprint_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, request)

        assert result.name == request.name
        assert result.goal == request.goal
        assert result.start_date == request.start_date
        assert result.end_date == request.end_date
        assert result.status == request.status
        mock_sprint_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sprint_project_not_found(
        self,
        mock_sprint_repository,
        mock_project_repository,
    ):
        """Test sprint creation when project not found."""
        request = CreateSprintRequest(name="Sprint 1")
        mock_project_repository.get_by_id.return_value = None

        use_case = CreateSprintUseCase(mock_sprint_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), request)

    @pytest.mark.asyncio
    async def test_create_sprint_overlapping_dates(
        self,
        mock_sprint_repository,
        mock_project_repository,
        test_project,
        test_sprint,
    ):
        """Test sprint creation with overlapping dates."""
        request = CreateSprintRequest(
            name="Sprint 2",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 20),
        )

        mock_project_repository.get_by_id.return_value = test_project
        mock_sprint_repository.find_overlapping_sprints.return_value = [test_sprint]

        use_case = CreateSprintUseCase(mock_sprint_repository, mock_project_repository)

        with pytest.raises(ConflictException):
            await use_case.execute(test_project.id, request)

    @pytest.mark.asyncio
    async def test_create_sprint_invalid_dates(
        self,
        mock_sprint_repository,
        mock_project_repository,
        test_project,
    ):
        """Test sprint creation with invalid dates."""
        request = CreateSprintRequest(
            name="Sprint 1",
            start_date=date(2024, 1, 14),
            end_date=date(2024, 1, 1),  # End before start
        )

        mock_project_repository.get_by_id.return_value = test_project

        use_case = CreateSprintUseCase(mock_sprint_repository, mock_project_repository)

        with pytest.raises(ValueError, match="start date must be before end date"):
            await use_case.execute(test_project.id, request)


class TestGetSprintUseCase:
    """Tests for GetSprintUseCase."""

    @pytest.mark.asyncio
    async def test_get_sprint_success(
        self,
        mock_sprint_repository,
        test_sprint,
    ):
        """Test successful sprint retrieval."""
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = []

        use_case = GetSprintUseCase(mock_sprint_repository)
        result = await use_case.execute(test_sprint.id)

        assert result.id == test_sprint.id
        assert result.name == test_sprint.name
        assert result.issues == []
        mock_sprint_repository.get_by_id.assert_called_once_with(test_sprint.id)

    @pytest.mark.asyncio
    async def test_get_sprint_not_found(
        self,
        mock_sprint_repository,
    ):
        """Test sprint retrieval when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None

        use_case = GetSprintUseCase(mock_sprint_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4())


class TestListSprintsUseCase:
    """Tests for ListSprintsUseCase."""

    @pytest.mark.asyncio
    async def test_list_sprints_success(
        self,
        mock_sprint_repository,
        mock_project_repository,
        test_project,
        test_sprint,
    ):
        """Test successful sprint listing."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_sprint_repository.get_all.return_value = [test_sprint]
        mock_sprint_repository.count.return_value = 1

        use_case = ListSprintsUseCase(mock_sprint_repository, mock_project_repository)
        result = await use_case.execute(test_project.id, page=1, limit=20)

        assert result.total == 1
        assert len(result.sprints) == 1
        assert result.sprints[0].id == test_sprint.id
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_sprints_with_status_filter(
        self,
        mock_sprint_repository,
        mock_project_repository,
        test_project,
        test_sprint,
    ):
        """Test sprint listing with status filter."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_sprint_repository.get_all.return_value = [test_sprint]
        mock_sprint_repository.count.return_value = 1

        use_case = ListSprintsUseCase(mock_sprint_repository, mock_project_repository)
        result = await use_case.execute(
            test_project.id,
            page=1,
            limit=20,
            status=SprintStatus.PLANNED,
        )

        assert result.total == 1
        mock_sprint_repository.get_all.assert_called_once_with(
            project_id=test_project.id,
            page=1,
            limit=20,
            status=SprintStatus.PLANNED,
        )

    @pytest.mark.asyncio
    async def test_list_sprints_project_not_found(
        self,
        mock_sprint_repository,
        mock_project_repository,
    ):
        """Test sprint listing when project not found."""
        mock_project_repository.get_by_id.return_value = None

        use_case = ListSprintsUseCase(mock_sprint_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4())


class TestUpdateSprintUseCase:
    """Tests for UpdateSprintUseCase."""

    @pytest.mark.asyncio
    async def test_update_sprint_success(
        self,
        mock_sprint_repository,
        test_sprint,
    ):
        """Test successful sprint update."""
        request = UpdateSprintRequest(name="Updated Sprint Name")
        updated_sprint = Sprint.create(
            project_id=test_sprint.project_id,
            name="Updated Sprint Name",
            goal=test_sprint.goal,
            start_date=test_sprint.start_date,
            end_date=test_sprint.end_date,
            status=test_sprint.status,
        )
        updated_sprint.id = test_sprint.id

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.find_overlapping_sprints.return_value = []
        mock_sprint_repository.update.return_value = updated_sprint

        use_case = UpdateSprintUseCase(mock_sprint_repository)
        result = await use_case.execute(test_sprint.id, request)

        assert result.name == "Updated Sprint Name"
        mock_sprint_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_sprint_not_found(
        self,
        mock_sprint_repository,
    ):
        """Test sprint update when sprint not found."""
        request = UpdateSprintRequest(name="Updated Name")
        mock_sprint_repository.get_by_id.return_value = None

        use_case = UpdateSprintUseCase(mock_sprint_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), request)

    @pytest.mark.asyncio
    async def test_update_sprint_overlapping_dates(
        self,
        mock_sprint_repository,
        test_sprint,
    ):
        """Test sprint update with overlapping dates."""
        overlapping_sprint = Sprint.create(
            project_id=test_sprint.project_id,
            name="Overlapping Sprint",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 20),
        )

        request = UpdateSprintRequest(
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 15),
        )

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.find_overlapping_sprints.return_value = [overlapping_sprint]

        use_case = UpdateSprintUseCase(mock_sprint_repository)

        with pytest.raises(ConflictException):
            await use_case.execute(test_sprint.id, request)


class TestDeleteSprintUseCase:
    """Tests for DeleteSprintUseCase."""

    @pytest.mark.asyncio
    async def test_delete_sprint_success(
        self,
        mock_sprint_repository,
        test_sprint,
    ):
        """Test successful sprint deletion."""
        mock_sprint_repository.get_by_id.return_value = test_sprint

        use_case = DeleteSprintUseCase(mock_sprint_repository)
        await use_case.execute(test_sprint.id)

        mock_sprint_repository.delete.assert_called_once_with(test_sprint.id)

    @pytest.mark.asyncio
    async def test_delete_sprint_not_found(
        self,
        mock_sprint_repository,
    ):
        """Test sprint deletion when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None

        use_case = DeleteSprintUseCase(mock_sprint_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4())


@pytest.fixture
def test_issue(test_project):
    """Create a test issue."""
    return Issue.create(
        project_id=test_project.id,
        issue_number=1,
        title="Test Issue",
        description="Test description",
    )


class TestAddIssueToSprintUseCase:
    """Tests for AddIssueToSprintUseCase."""

    @pytest.mark.asyncio
    async def test_add_issue_to_sprint_success(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        test_sprint,
        test_issue,
    ):
        """Test successful adding issue to sprint."""
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_sprint_repository.get_issue_sprint.return_value = None

        use_case = AddIssueToSprintUseCase(mock_sprint_repository, mock_issue_repository)
        await use_case.execute(test_sprint.id, test_issue.id, order=1)

        mock_sprint_repository.add_issue_to_sprint.assert_called_once_with(
            test_sprint.id, test_issue.id, 1
        )

    @pytest.mark.asyncio
    async def test_add_issue_to_sprint_sprint_not_found(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        test_issue,
    ):
        """Test adding issue when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None

        use_case = AddIssueToSprintUseCase(mock_sprint_repository, mock_issue_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), test_issue.id)

    @pytest.mark.asyncio
    async def test_add_issue_to_sprint_issue_not_found(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        test_sprint,
    ):
        """Test adding issue when issue not found."""
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_issue_repository.get_by_id.return_value = None

        use_case = AddIssueToSprintUseCase(mock_sprint_repository, mock_issue_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(test_sprint.id, uuid4())

    @pytest.mark.asyncio
    async def test_add_issue_to_sprint_different_project(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        test_sprint,
    ):
        """Test adding issue from different project."""
        different_project_issue = Issue.create(
            project_id=uuid4(),  # Different project
            issue_number=1,
            title="Different Project Issue",
        )

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_issue_repository.get_by_id.return_value = different_project_issue

        use_case = AddIssueToSprintUseCase(mock_sprint_repository, mock_issue_repository)

        with pytest.raises(ConflictException, match="different project"):
            await use_case.execute(test_sprint.id, different_project_issue.id)

    @pytest.mark.asyncio
    async def test_add_issue_to_sprint_already_in_active_sprint(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        test_sprint,
        test_issue,
    ):
        """Test adding issue that is already in an active sprint."""
        active_sprint = Sprint.create(
            project_id=test_sprint.project_id,
            name="Active Sprint",
            status=SprintStatus.ACTIVE,
        )

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_sprint_repository.get_issue_sprint.return_value = active_sprint

        use_case = AddIssueToSprintUseCase(mock_sprint_repository, mock_issue_repository)

        with pytest.raises(ConflictException, match="already in active sprint"):
            await use_case.execute(test_sprint.id, test_issue.id)


class TestRemoveIssueFromSprintUseCase:
    """Tests for RemoveIssueFromSprintUseCase."""

    @pytest.mark.asyncio
    async def test_remove_issue_from_sprint_success(
        self,
        mock_sprint_repository,
        test_sprint,
        test_issue,
    ):
        """Test successful removing issue from sprint."""
        mock_sprint_repository.get_by_id.return_value = test_sprint

        use_case = RemoveIssueFromSprintUseCase(mock_sprint_repository)
        await use_case.execute(test_sprint.id, test_issue.id)

        mock_sprint_repository.remove_issue_from_sprint.assert_called_once_with(
            test_sprint.id, test_issue.id
        )

    @pytest.mark.asyncio
    async def test_remove_issue_from_sprint_sprint_not_found(
        self,
        mock_sprint_repository,
        test_issue,
    ):
        """Test removing issue when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None

        use_case = RemoveIssueFromSprintUseCase(mock_sprint_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), test_issue.id)


class TestReorderSprintIssuesUseCase:
    """Tests for ReorderSprintIssuesUseCase."""

    @pytest.mark.asyncio
    async def test_reorder_sprint_issues_success(
        self,
        mock_sprint_repository,
        test_sprint,
        test_issue,
    ):
        """Test successful reordering sprint issues."""
        mock_sprint_repository.get_by_id.return_value = test_sprint
        issue_orders = {test_issue.id: 1}

        use_case = ReorderSprintIssuesUseCase(mock_sprint_repository)
        await use_case.execute(test_sprint.id, issue_orders)

        mock_sprint_repository.reorder_sprint_issues.assert_called_once_with(
            test_sprint.id, issue_orders
        )

    @pytest.mark.asyncio
    async def test_reorder_sprint_issues_sprint_not_found(
        self,
        mock_sprint_repository,
        test_issue,
    ):
        """Test reordering issues when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None
        issue_orders = {test_issue.id: 1}

        use_case = ReorderSprintIssuesUseCase(mock_sprint_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), issue_orders)


class TestGetSprintMetricsUseCase:
    """Tests for GetSprintMetricsUseCase."""

    @pytest.mark.asyncio
    async def test_get_sprint_metrics_success(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
        test_sprint,
    ):
        """Test successful getting sprint metrics."""
        from datetime import datetime
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        # Setup sprint with dates
        test_sprint.start_date = date(2024, 1, 1)
        test_sprint.end_date = date(2024, 1, 14)
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = [
            (uuid4(), 0),
            (uuid4(), 1),
        ]

        # Mock issues
        issue1 = MagicMock(spec=IssueModel)
        issue1.id = uuid4()
        issue1.story_points = 5
        issue1.status = "todo"
        issue1.updated_at = None
        issue1.deleted_at = None

        issue2 = MagicMock(spec=IssueModel)
        issue2.id = uuid4()
        issue2.story_points = 3
        issue2.status = "done"
        issue2.updated_at = datetime(2024, 1, 5)
        issue2.deleted_at = None

        # Mock session execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [issue1, issue2]
        mock_session.execute.return_value = mock_result

        use_case = GetSprintMetricsUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )
        result = await use_case.execute(test_sprint.id)

        assert result.sprint_id == test_sprint.id
        assert result.total_story_points == 8
        assert result.completed_story_points == 3
        assert result.remaining_story_points == 5
        assert result.completion_percentage == 37.5
        assert result.velocity == 3.0
        assert result.issue_counts == {"todo": 1, "done": 1}
        assert len(result.burndown_data) > 0

    @pytest.mark.asyncio
    async def test_get_sprint_metrics_no_issues(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
        test_sprint,
    ):
        """Test getting metrics for sprint with no issues."""
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = []

        use_case = GetSprintMetricsUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )
        result = await use_case.execute(test_sprint.id)

        assert result.sprint_id == test_sprint.id
        assert result.total_story_points == 0
        assert result.completed_story_points == 0
        assert result.remaining_story_points == 0
        assert result.completion_percentage == 0.0
        assert result.velocity == 0.0
        assert result.issue_counts == {}
        assert result.burndown_data == []

    @pytest.mark.asyncio
    async def test_get_sprint_metrics_sprint_not_found(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
    ):
        """Test getting metrics when sprint not found."""
        mock_sprint_repository.get_by_id.return_value = None

        use_case = GetSprintMetricsUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_get_sprint_metrics_no_dates(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
        test_sprint,
    ):
        """Test getting metrics for sprint without dates."""
        test_sprint.start_date = None
        test_sprint.end_date = None
        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = [(uuid4(), 0)]

        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        issue = MagicMock(spec=IssueModel)
        issue.id = uuid4()
        issue.story_points = 5
        issue.status = "todo"
        issue.updated_at = None
        issue.deleted_at = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [issue]
        mock_session.execute.return_value = mock_result

        use_case = GetSprintMetricsUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )
        result = await use_case.execute(test_sprint.id)

        assert result.burndown_data == []


class TestCompleteSprintUseCase:
    """Tests for CompleteSprintUseCase."""

    @pytest.mark.asyncio
    async def test_complete_sprint_success(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
        test_sprint,
    ):
        """Test successful sprint completion."""
        from src.application.dtos.sprint_metrics import CompleteSprintRequest
        from unittest.mock import MagicMock

        from src.infrastructure.database.models import IssueModel

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = [(uuid4(), 0)]

        # Mock issue
        issue = MagicMock(spec=IssueModel)
        issue.id = uuid4()
        issue.status = "todo"
        issue.deleted_at = None
        issue.backlog_order = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [issue]
        mock_session.execute.return_value = mock_result

        # Mock metrics use case
        from src.application.dtos.sprint_metrics import SprintMetricsResponse

        mock_metrics = SprintMetricsResponse(
            sprint_id=test_sprint.id,
            total_story_points=5,
            completed_story_points=0,
            remaining_story_points=5,
            completion_percentage=0.0,
            velocity=0.0,
            issue_counts={},
            burndown_data=[],
        )

        request = CompleteSprintRequest(move_incomplete_to_backlog=True)

        use_case = CompleteSprintUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )

        # Mock the metrics use case
        with patch(
            "src.application.use_cases.sprint.get_sprint_metrics.GetSprintMetricsUseCase"
        ) as mock_metrics_class:
            mock_metrics_instance = AsyncMock()
            mock_metrics_instance.execute.return_value = mock_metrics
            mock_metrics_class.return_value = mock_metrics_instance

            result = await use_case.execute(test_sprint.id, request)
            assert result.sprint_id == test_sprint.id
            assert result.incomplete_issues_moved == 1
            assert result.metrics == mock_metrics
            assert test_sprint.status == SprintStatus.COMPLETED
            mock_sprint_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_sprint_no_move_incomplete(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
        test_sprint,
    ):
        """Test sprint completion without moving incomplete issues."""
        from src.application.dtos.sprint_metrics import (
            CompleteSprintRequest,
            SprintMetricsResponse,
        )

        mock_sprint_repository.get_by_id.return_value = test_sprint
        mock_sprint_repository.get_sprint_issues.return_value = []

        mock_metrics = SprintMetricsResponse(
            sprint_id=test_sprint.id,
            total_story_points=0,
            completed_story_points=0,
            remaining_story_points=0,
            completion_percentage=0.0,
            velocity=0.0,
            issue_counts={},
            burndown_data=[],
        )

        request = CompleteSprintRequest(move_incomplete_to_backlog=False)

        use_case = CompleteSprintUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )

        # Mock the metrics use case
        with patch(
            "src.application.use_cases.sprint.get_sprint_metrics.GetSprintMetricsUseCase"
        ) as mock_metrics_class:
            mock_metrics_instance = AsyncMock()
            mock_metrics_instance.execute.return_value = mock_metrics
            mock_metrics_class.return_value = mock_metrics_instance

            result = await use_case.execute(test_sprint.id, request)
            assert result.sprint_id == test_sprint.id
            assert result.incomplete_issues_moved == 0
            assert test_sprint.status == SprintStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_complete_sprint_sprint_not_found(
        self,
        mock_sprint_repository,
        mock_issue_repository,
        mock_session,
    ):
        """Test completing sprint when sprint not found."""
        from src.application.dtos.sprint_metrics import CompleteSprintRequest

        mock_sprint_repository.get_by_id.return_value = None
        request = CompleteSprintRequest()

        use_case = CompleteSprintUseCase(
            mock_sprint_repository, mock_issue_repository, mock_session
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(uuid4(), request)
