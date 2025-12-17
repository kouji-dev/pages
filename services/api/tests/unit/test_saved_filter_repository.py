"""Unit tests for SavedFilterRepository implementation."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.saved_filter import SavedFilter
from src.infrastructure.database.models.saved_filter import SavedFilterModel
from src.infrastructure.database.repositories.saved_filter_repository import (
    SQLAlchemySavedFilterRepository,
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
def test_saved_filter(test_project_id, test_user_id):
    """Create a test saved filter entity."""
    return SavedFilter.create(
        project_id=test_project_id,
        user_id=test_user_id,
        name="My Filter",
        filter_criteria={"status": "todo", "priority": "high"},
    )


@pytest.mark.asyncio
async def test_create_saved_filter(mock_session, test_saved_filter):
    """Test creating a saved filter."""
    filter_model = SavedFilterModel(
        id=test_saved_filter.id,
        project_id=test_saved_filter.project_id,
        user_id=test_saved_filter.user_id,
        name=test_saved_filter.name,
        filter_criteria=test_saved_filter.filter_criteria,
        created_at=test_saved_filter.created_at,
        updated_at=test_saved_filter.updated_at,
    )

    mock_result = create_mock_result(scalar_value=filter_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemySavedFilterRepository(mock_session)
    created = await repository.create(test_saved_filter)

    assert created is not None
    assert created.id == test_saved_filter.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_saved_filter_by_id_found(mock_session, test_saved_filter):
    """Test getting saved filter by ID when found."""
    filter_model = SavedFilterModel(
        id=test_saved_filter.id,
        project_id=test_saved_filter.project_id,
        user_id=test_saved_filter.user_id,
        name=test_saved_filter.name,
        filter_criteria=test_saved_filter.filter_criteria,
        created_at=test_saved_filter.created_at,
        updated_at=test_saved_filter.updated_at,
    )

    mock_result = create_mock_result(scalar_value=filter_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemySavedFilterRepository(mock_session)
    found = await repository.get_by_id(test_saved_filter.id)

    assert found is not None
    assert found.id == test_saved_filter.id


@pytest.mark.asyncio
async def test_get_saved_filter_by_id_not_found(mock_session):
    """Test getting saved filter by ID when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemySavedFilterRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_saved_filters_by_project_id(mock_session, test_project_id, test_saved_filter):
    """Test getting saved filters by project ID."""
    filter_model = SavedFilterModel(
        id=test_saved_filter.id,
        project_id=test_saved_filter.project_id,
        user_id=test_saved_filter.user_id,
        name=test_saved_filter.name,
        filter_criteria=test_saved_filter.filter_criteria,
        created_at=test_saved_filter.created_at,
        updated_at=test_saved_filter.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[filter_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemySavedFilterRepository(mock_session)
    # Use get_by_user_and_project instead
    filters = await repository.get_by_user_and_project(test_saved_filter.user_id, test_project_id)

    assert len(filters) == 1
    assert filters[0].id == test_saved_filter.id


@pytest.mark.asyncio
async def test_get_saved_filters_by_user_id(mock_session, test_user_id, test_saved_filter):
    """Test getting saved filters by user ID."""
    filter_model = SavedFilterModel(
        id=test_saved_filter.id,
        project_id=test_saved_filter.project_id,
        user_id=test_saved_filter.user_id,
        name=test_saved_filter.name,
        filter_criteria=test_saved_filter.filter_criteria,
        created_at=test_saved_filter.created_at,
        updated_at=test_saved_filter.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[filter_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemySavedFilterRepository(mock_session)
    filters = await repository.get_by_user_id(test_user_id)

    assert len(filters) == 1
    assert filters[0].id == test_saved_filter.id
