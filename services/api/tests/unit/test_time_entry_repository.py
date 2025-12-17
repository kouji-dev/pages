"""Unit tests for TimeEntryRepository implementation."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.time_entry import TimeEntry
from src.infrastructure.database.models.time_entry import TimeEntryModel
from src.infrastructure.database.repositories.time_entry_repository import (
    SQLAlchemyTimeEntryRepository,
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
def test_time_entry():
    """Create a test time entry entity."""
    return TimeEntry.create(
        issue_id=uuid4(),
        user_id=uuid4(),
        hours=Decimal("2.5"),
        date=date.today(),
        description="Worked on feature",
    )


@pytest.mark.asyncio
async def test_create_time_entry(mock_session, test_time_entry):
    """Test creating a time entry."""
    entry_model = TimeEntryModel(
        id=test_time_entry.id,
        issue_id=test_time_entry.issue_id,
        user_id=test_time_entry.user_id,
        hours=test_time_entry.hours,
        date=test_time_entry.date,
        description=test_time_entry.description,
        created_at=test_time_entry.created_at,
        updated_at=test_time_entry.updated_at,
    )

    mock_result = create_mock_result(scalar_value=entry_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyTimeEntryRepository(mock_session)
    created = await repository.create(test_time_entry)

    assert created is not None
    assert created.id == test_time_entry.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_time_entry_by_id_found(mock_session, test_time_entry):
    """Test getting time entry by ID when found."""
    entry_model = TimeEntryModel(
        id=test_time_entry.id,
        issue_id=test_time_entry.issue_id,
        user_id=test_time_entry.user_id,
        hours=test_time_entry.hours,
        date=test_time_entry.date,
        description=test_time_entry.description,
        created_at=test_time_entry.created_at,
        updated_at=test_time_entry.updated_at,
    )

    mock_result = create_mock_result(scalar_value=entry_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyTimeEntryRepository(mock_session)
    found = await repository.get_by_id(test_time_entry.id)

    assert found is not None
    assert found.id == test_time_entry.id


@pytest.mark.asyncio
async def test_get_time_entry_by_id_not_found(mock_session):
    """Test getting time entry by ID when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyTimeEntryRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_time_entries_by_issue_id(mock_session, test_time_entry):
    """Test getting time entries by issue ID."""
    entry_model = TimeEntryModel(
        id=test_time_entry.id,
        issue_id=test_time_entry.issue_id,
        user_id=test_time_entry.user_id,
        hours=test_time_entry.hours,
        date=test_time_entry.date,
        description=test_time_entry.description,
        created_at=test_time_entry.created_at,
        updated_at=test_time_entry.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[entry_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyTimeEntryRepository(mock_session)
    entries = await repository.get_by_issue_id(test_time_entry.issue_id)

    assert len(entries) == 1
    assert entries[0].id == test_time_entry.id


@pytest.mark.asyncio
async def test_get_time_entries_by_user_id(mock_session, test_time_entry):
    """Test getting time entries by user ID."""
    entry_model = TimeEntryModel(
        id=test_time_entry.id,
        issue_id=test_time_entry.issue_id,
        user_id=test_time_entry.user_id,
        hours=test_time_entry.hours,
        date=test_time_entry.date,
        description=test_time_entry.description,
        created_at=test_time_entry.created_at,
        updated_at=test_time_entry.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[entry_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyTimeEntryRepository(mock_session)
    entries = await repository.get_by_user_id(test_time_entry.user_id)

    assert len(entries) == 1
    assert entries[0].id == test_time_entry.id
