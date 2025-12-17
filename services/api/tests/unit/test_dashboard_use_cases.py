"""Unit tests for dashboard use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.dashboard import (
    CreateDashboardRequest,
    DashboardWidgetRequest,
    UpdateDashboardRequest,
)
from src.application.use_cases.dashboard import (
    CreateDashboardUseCase,
    DeleteDashboardUseCase,
    GetDashboardUseCase,
    GetWidgetDataUseCase,
    ListDashboardsUseCase,
    UpdateDashboardUseCase,
)
from src.domain.entities import Dashboard, Project
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_dashboard_repository():
    """Mock dashboard repository."""
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
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
        description="A test project",
    )


@pytest.fixture
def test_dashboard(test_project):
    """Create a test dashboard."""
    dashboard = Dashboard.create(
        project_id=test_project.id,
        user_id=uuid4(),
        name="Test Dashboard",
    )
    dashboard.add_widget("issue_status_breakdown", {})
    return dashboard


class TestCreateDashboardUseCase:
    """Tests for CreateDashboardUseCase."""

    @pytest.mark.asyncio
    async def test_create_dashboard_success(
        self,
        mock_dashboard_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful dashboard creation."""
        user_id = uuid4()
        request = CreateDashboardRequest(
            name="Test Dashboard",
            project_id=test_project.id,
            widgets=[DashboardWidgetRequest(type="issue_status_breakdown", config={})],
        )

        mock_project_repository.get_by_id.return_value = test_project

        created_dashboard = Dashboard.create(
            project_id=test_project.id,
            user_id=user_id,
            name=request.name,
        )
        created_dashboard.add_widget("issue_status_breakdown", {})

        mock_dashboard_repository.create.return_value = created_dashboard

        use_case = CreateDashboardUseCase(mock_dashboard_repository, mock_project_repository)

        result = await use_case.execute(user_id, request)

        assert result.name == "Test Dashboard"
        assert result.project_id == test_project.id
        assert len(result.widgets) == 1
        mock_dashboard_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_dashboard_project_not_found(
        self,
        mock_dashboard_repository,
        mock_project_repository,
    ):
        """Test dashboard creation with non-existent project."""
        user_id = uuid4()
        request = CreateDashboardRequest(name="Test Dashboard", project_id=uuid4())

        mock_project_repository.get_by_id.return_value = None

        use_case = CreateDashboardUseCase(mock_dashboard_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(user_id, request)


class TestGetDashboardUseCase:
    """Tests for GetDashboardUseCase."""

    @pytest.mark.asyncio
    async def test_get_dashboard_success(self, mock_dashboard_repository, test_dashboard):
        """Test successfully getting a dashboard."""
        mock_dashboard_repository.get_by_id.return_value = test_dashboard

        use_case = GetDashboardUseCase(mock_dashboard_repository)

        result = await use_case.execute(test_dashboard.id)

        assert result.id == test_dashboard.id
        assert result.name == test_dashboard.name
        mock_dashboard_repository.get_by_id.assert_called_once_with(test_dashboard.id)

    @pytest.mark.asyncio
    async def test_get_dashboard_not_found(self, mock_dashboard_repository):
        """Test getting non-existent dashboard."""
        dashboard_id = uuid4()
        mock_dashboard_repository.get_by_id.return_value = None

        use_case = GetDashboardUseCase(mock_dashboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(dashboard_id)


class TestListDashboardsUseCase:
    """Tests for ListDashboardsUseCase."""

    @pytest.mark.asyncio
    async def test_list_dashboards_success(self, mock_dashboard_repository, test_dashboard):
        """Test successfully listing dashboards."""
        dashboards = [test_dashboard]
        mock_dashboard_repository.get_by_user_id.return_value = dashboards

        use_case = ListDashboardsUseCase(mock_dashboard_repository)

        result = await use_case.execute(test_dashboard.user_id, None)

        assert result.total == 1
        assert len(result.dashboards) == 1
        assert result.dashboards[0].id == test_dashboard.id


class TestUpdateDashboardUseCase:
    """Tests for UpdateDashboardUseCase."""

    @pytest.mark.asyncio
    async def test_update_dashboard_success(self, mock_dashboard_repository, test_dashboard):
        """Test successfully updating a dashboard."""
        request = UpdateDashboardRequest(name="Updated Dashboard")

        updated_dashboard = Dashboard.create(
            project_id=test_dashboard.project_id,
            user_id=test_dashboard.user_id,
            name=request.name,
        )

        mock_dashboard_repository.get_by_id.return_value = test_dashboard
        mock_dashboard_repository.update.return_value = updated_dashboard

        use_case = UpdateDashboardUseCase(mock_dashboard_repository)

        result = await use_case.execute(test_dashboard.id, request)

        assert result.name == "Updated Dashboard"
        mock_dashboard_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_dashboard_not_found(self, mock_dashboard_repository):
        """Test updating non-existent dashboard."""
        dashboard_id = uuid4()
        request = UpdateDashboardRequest(name="Updated Dashboard")

        mock_dashboard_repository.get_by_id.return_value = None

        use_case = UpdateDashboardUseCase(mock_dashboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(dashboard_id, request)


class TestDeleteDashboardUseCase:
    """Tests for DeleteDashboardUseCase."""

    @pytest.mark.asyncio
    async def test_delete_dashboard_success(self, mock_dashboard_repository, test_dashboard):
        """Test successfully deleting a dashboard."""
        mock_dashboard_repository.get_by_id.return_value = test_dashboard
        mock_dashboard_repository.delete.return_value = None

        use_case = DeleteDashboardUseCase(mock_dashboard_repository)

        await use_case.execute(test_dashboard.id)

        mock_dashboard_repository.delete.assert_called_once_with(test_dashboard.id)

    @pytest.mark.asyncio
    async def test_delete_dashboard_not_found(self, mock_dashboard_repository):
        """Test deleting non-existent dashboard."""
        dashboard_id = uuid4()
        mock_dashboard_repository.get_by_id.return_value = None

        use_case = DeleteDashboardUseCase(mock_dashboard_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(dashboard_id)


class TestGetWidgetDataUseCase:
    """Tests for GetWidgetDataUseCase."""

    @pytest.fixture
    def mock_session(self):
        """Mock async session."""
        from unittest.mock import AsyncMock, MagicMock

        session = MagicMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_widget_data_issue_status_breakdown(
        self,
        mock_dashboard_repository,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
        test_dashboard,
    ):
        """Test getting widget data for issue status breakdown."""
        from unittest.mock import MagicMock

        from src.application.dtos.dashboard import WidgetDataRequest

        widget_id = test_dashboard.widgets[0].id if test_dashboard.widgets else uuid4()
        request = WidgetDataRequest(widget_type="issue_status_breakdown")

        mock_dashboard_repository.get_by_id.return_value = test_dashboard

        # Mock SQL result
        mock_row = MagicMock()
        mock_row.status = "todo"
        mock_row.count = 5
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        use_case = GetWidgetDataUseCase(
            mock_dashboard_repository,
            mock_issue_repository,
            mock_project_repository,
            mock_session,
        )

        result = await use_case.execute(test_dashboard.id, widget_id, request)

        assert result.data == {"todo": 5}
        mock_dashboard_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_widget_data_dashboard_not_found(
        self,
        mock_dashboard_repository,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
    ):
        """Test getting widget data for non-existent dashboard."""
        from src.application.dtos.dashboard import WidgetDataRequest

        dashboard_id = uuid4()
        widget_id = uuid4()
        request = WidgetDataRequest(widget_type="issue_status_breakdown")

        mock_dashboard_repository.get_by_id.return_value = None

        use_case = GetWidgetDataUseCase(
            mock_dashboard_repository,
            mock_issue_repository,
            mock_project_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(dashboard_id, widget_id, request)

    @pytest.mark.asyncio
    async def test_get_widget_data_widget_not_found(
        self,
        mock_dashboard_repository,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
        test_dashboard,
    ):
        """Test getting widget data for non-existent widget."""
        from src.application.dtos.dashboard import WidgetDataRequest

        widget_id = uuid4()
        request = WidgetDataRequest(widget_type="issue_status_breakdown")

        mock_dashboard_repository.get_by_id.return_value = test_dashboard

        use_case = GetWidgetDataUseCase(
            mock_dashboard_repository,
            mock_issue_repository,
            mock_project_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(test_dashboard.id, widget_id, request)

    @pytest.mark.asyncio
    async def test_get_widget_data_no_project(
        self,
        mock_dashboard_repository,
        mock_issue_repository,
        mock_project_repository,
        mock_session,
    ):
        """Test getting widget data when no project is specified."""
        from src.application.dtos.dashboard import WidgetDataRequest
        from src.domain.entities import DashboardWidget

        dashboard = Dashboard.create(
            project_id=None,
            user_id=uuid4(),
            name="Test Dashboard",
        )
        widget = DashboardWidget.create(
            dashboard_id=dashboard.id,
            type="issue_status_breakdown",
            position=0,
        )
        dashboard.widgets = [widget]

        widget_id = widget.id
        request = WidgetDataRequest(widget_type="issue_status_breakdown")

        mock_dashboard_repository.get_by_id.return_value = dashboard

        use_case = GetWidgetDataUseCase(
            mock_dashboard_repository,
            mock_issue_repository,
            mock_project_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(dashboard.id, widget_id, request)
