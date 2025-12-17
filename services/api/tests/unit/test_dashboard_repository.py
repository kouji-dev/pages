"""Unit tests for DashboardRepository implementation."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.dashboard import Dashboard, DashboardWidget
from src.infrastructure.database.models.dashboard import DashboardModel
from src.infrastructure.database.repositories.dashboard_repository import (
    SQLAlchemyDashboardRepository,
)
from tests.unit.test_repository_helpers import create_mock_result


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = MagicMock(spec=AsyncSession)
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.scalar_one_or_none = AsyncMock()
    session.scalars = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def test_project_id():
    """Get a test project ID."""
    return uuid4()


@pytest.fixture
def test_user_id():
    """Get a test user ID."""
    return uuid4()


@pytest.fixture
def test_dashboard(test_project_id, test_user_id):
    """Create a test dashboard entity."""
    dashboard = Dashboard.create(
        project_id=test_project_id,
        user_id=test_user_id,
        name="Test Dashboard",
    )

    # Add widget
    widget = DashboardWidget.create(
        dashboard_id=dashboard.id,
        type="issue_status_breakdown",
        position=0,
        config={"key": "value"},
    )
    dashboard.widgets = [widget]

    return dashboard


@pytest.mark.asyncio
async def test_create_dashboard(mock_session, test_dashboard):
    """Test creating a dashboard."""
    dashboard_model = DashboardModel(
        id=test_dashboard.id,
        project_id=test_dashboard.project_id,
        user_id=test_dashboard.user_id,
        name=test_dashboard.name,
        created_at=test_dashboard.created_at,
        updated_at=test_dashboard.updated_at,
    )
    dashboard_model.widgets = []

    # create() calls _get_by_id() after creation, so we need to mock that call too
    mock_result = create_mock_result(scalar_value=dashboard_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyDashboardRepository(mock_session)
    created = await repository.create(test_dashboard)

    assert created is not None
    assert created.id == test_dashboard.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_dashboard_by_id_found(mock_session, test_dashboard):
    """Test getting dashboard by ID when found."""
    dashboard_model = DashboardModel(
        id=test_dashboard.id,
        project_id=test_dashboard.project_id,
        user_id=test_dashboard.user_id,
        name=test_dashboard.name,
        created_at=test_dashboard.created_at,
        updated_at=test_dashboard.updated_at,
    )
    dashboard_model.widgets = []

    mock_result = create_mock_result(scalar_value=dashboard_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyDashboardRepository(mock_session)
    found = await repository.get_by_id(test_dashboard.id)

    assert found is not None
    assert found.id == test_dashboard.id


@pytest.mark.asyncio
async def test_get_dashboard_by_id_not_found(mock_session):
    """Test getting dashboard by ID when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyDashboardRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_dashboards_by_project_id(mock_session, test_project_id, test_dashboard):
    """Test getting dashboards by project ID."""
    dashboard_model = DashboardModel(
        id=test_dashboard.id,
        project_id=test_dashboard.project_id,
        user_id=test_dashboard.user_id,
        name=test_dashboard.name,
        created_at=test_dashboard.created_at,
        updated_at=test_dashboard.updated_at,
    )
    dashboard_model.widgets = []

    mock_result = create_mock_result(scalars_list=[dashboard_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyDashboardRepository(mock_session)
    dashboards = await repository.get_by_project_id(test_project_id)

    assert len(dashboards) == 1
    assert dashboards[0].id == test_dashboard.id
