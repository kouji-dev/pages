"""Unit tests for time entry use cases."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.time_entry import TimeEntryRequest
from src.application.use_cases.time_entry import (
    CreateTimeEntryUseCase,
    DeleteTimeEntryUseCase,
    GetTimeEntryUseCase,
    GetTimeSummaryUseCase,
    ListTimeEntriesUseCase,
    UpdateTimeEntryUseCase,
)
from src.domain.entities import Issue, TimeEntry
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_time_entry_repository():
    """Mock time entry repository."""
    return AsyncMock()


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def test_issue():
    """Create a test issue."""
    return Issue.create(
        project_id=uuid4(),
        issue_number=1,
        title="Test Issue",
    )


@pytest.fixture
def test_time_entry(test_issue):
    """Create a test time entry."""
    return TimeEntry.create(
        issue_id=test_issue.id,
        user_id=uuid4(),
        hours=Decimal("2.5"),
        date=date.today(),
        description="Worked on feature",
    )


class TestCreateTimeEntryUseCase:
    """Tests for CreateTimeEntryUseCase."""

    @pytest.mark.asyncio
    async def test_create_time_entry_success(
        self,
        mock_time_entry_repository,
        mock_issue_repository,
        test_issue,
    ):
        """Test successful time entry creation."""
        user_id = uuid4()
        request = TimeEntryRequest(
            hours=Decimal("2.5"),
            date=date.today(),
            description="Worked on feature",
        )

        mock_issue_repository.get_by_id.return_value = test_issue

        created_entry = TimeEntry.create(
            issue_id=test_issue.id,
            user_id=user_id,
            hours=request.hours,
            date=request.date,
            description=request.description,
        )

        mock_time_entry_repository.create.return_value = created_entry

        use_case = CreateTimeEntryUseCase(mock_time_entry_repository, mock_issue_repository)

        result = await use_case.execute(test_issue.id, user_id, request)

        assert result.hours == Decimal("2.5")
        assert result.issue_id == test_issue.id
        mock_time_entry_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_time_entry_issue_not_found(
        self,
        mock_time_entry_repository,
        mock_issue_repository,
    ):
        """Test time entry creation with non-existent issue."""
        request = TimeEntryRequest(hours=Decimal("2.5"), date=date.today())
        issue_id = uuid4()
        user_id = uuid4()

        mock_issue_repository.get_by_id.return_value = None

        use_case = CreateTimeEntryUseCase(mock_time_entry_repository, mock_issue_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(issue_id, user_id, request)

    @pytest.mark.asyncio
    async def test_create_time_entry_invalid_hours(
        self,
        mock_time_entry_repository,
        mock_issue_repository,
        test_issue,
    ):
        """Test time entry creation with invalid hours."""
        from pydantic import ValidationError

        user_id = uuid4()

        mock_issue_repository.get_by_id.return_value = test_issue

        use_case = CreateTimeEntryUseCase(mock_time_entry_repository, mock_issue_repository)

        # Pydantic validates the request before it reaches the use case
        with pytest.raises(ValidationError):
            request = TimeEntryRequest(hours=Decimal("-1"), date=date.today())
            await use_case.execute(test_issue.id, user_id, request)


class TestGetTimeEntryUseCase:
    """Tests for GetTimeEntryUseCase."""

    @pytest.mark.asyncio
    async def test_get_time_entry_success(self, mock_time_entry_repository, test_time_entry):
        """Test successfully getting a time entry."""
        mock_time_entry_repository.get_by_id.return_value = test_time_entry

        use_case = GetTimeEntryUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_time_entry.id)

        assert result.id == test_time_entry.id
        assert result.hours == test_time_entry.hours
        mock_time_entry_repository.get_by_id.assert_called_once_with(test_time_entry.id)

    @pytest.mark.asyncio
    async def test_get_time_entry_not_found(self, mock_time_entry_repository):
        """Test getting non-existent time entry."""
        entry_id = uuid4()
        mock_time_entry_repository.get_by_id.return_value = None

        use_case = GetTimeEntryUseCase(mock_time_entry_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(entry_id)


class TestListTimeEntriesUseCase:
    """Tests for ListTimeEntriesUseCase."""

    @pytest.mark.asyncio
    async def test_list_time_entries_success(
        self, mock_time_entry_repository, test_issue, test_time_entry
    ):
        """Test successfully listing time entries."""
        entries = [test_time_entry]
        mock_time_entry_repository.get_by_issue_id.return_value = entries

        use_case = ListTimeEntriesUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_issue.id)

        assert result.total == 1
        assert len(result.entries) == 1
        assert result.entries[0].id == test_time_entry.id


class TestUpdateTimeEntryUseCase:
    """Tests for UpdateTimeEntryUseCase."""

    @pytest.mark.asyncio
    async def test_update_time_entry_success(self, mock_time_entry_repository, test_time_entry):
        """Test successfully updating a time entry."""
        request = TimeEntryRequest(hours=Decimal("3.0"), date=date.today())

        updated_entry = TimeEntry.create(
            issue_id=test_time_entry.issue_id,
            user_id=test_time_entry.user_id,
            hours=request.hours,
            date=request.date,
        )

        mock_time_entry_repository.get_by_id.return_value = test_time_entry
        mock_time_entry_repository.update.return_value = updated_entry

        use_case = UpdateTimeEntryUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_time_entry.id, request)

        assert result.hours == Decimal("3.0")
        mock_time_entry_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_time_entry_not_found(self, mock_time_entry_repository):
        """Test updating non-existent time entry."""
        entry_id = uuid4()
        request = TimeEntryRequest(hours=Decimal("3.0"), date=date.today())

        mock_time_entry_repository.get_by_id.return_value = None

        use_case = UpdateTimeEntryUseCase(mock_time_entry_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(entry_id, request)


class TestDeleteTimeEntryUseCase:
    """Tests for DeleteTimeEntryUseCase."""

    @pytest.mark.asyncio
    async def test_delete_time_entry_success(self, mock_time_entry_repository, test_time_entry):
        """Test successfully deleting a time entry."""
        mock_time_entry_repository.get_by_id.return_value = test_time_entry
        mock_time_entry_repository.delete.return_value = None

        use_case = DeleteTimeEntryUseCase(mock_time_entry_repository)

        await use_case.execute(test_time_entry.id)

        mock_time_entry_repository.delete.assert_called_once_with(test_time_entry.id)

    @pytest.mark.asyncio
    async def test_delete_time_entry_not_found(self, mock_time_entry_repository):
        """Test deleting non-existent time entry."""
        entry_id = uuid4()
        mock_time_entry_repository.get_by_id.return_value = None

        use_case = DeleteTimeEntryUseCase(mock_time_entry_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(entry_id)


class TestGetTimeSummaryUseCase:
    """Tests for GetTimeSummaryUseCase."""

    @pytest.mark.asyncio
    async def test_get_time_summary_success(
        self, mock_time_entry_repository, test_issue, test_time_entry
    ):
        """Test successfully getting time summary."""
        entries = [test_time_entry]
        mock_time_entry_repository.get_by_issue_id.return_value = entries
        mock_time_entry_repository.get_total_hours_by_issue.return_value = Decimal("2.5")

        use_case = GetTimeSummaryUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_issue.id)

        assert result.total_hours == Decimal("2.5")
        assert len(result.hours_by_user) > 0

    @pytest.mark.asyncio
    async def test_get_time_summary_multiple_entries(self, mock_time_entry_repository, test_issue):
        """Test getting time summary with multiple entries."""
        user_id1 = uuid4()
        user_id2 = uuid4()
        entry1 = TimeEntry.create(
            issue_id=test_issue.id,
            user_id=user_id1,
            hours=Decimal("2.5"),
            date=date.today(),
        )
        entry2 = TimeEntry.create(
            issue_id=test_issue.id,
            user_id=user_id2,
            hours=Decimal("1.5"),
            date=date.today(),
        )
        entry3 = TimeEntry.create(
            issue_id=test_issue.id,
            user_id=user_id1,
            hours=Decimal("1.0"),
            date=date.today(),
        )

        entries = [entry1, entry2, entry3]
        mock_time_entry_repository.get_by_issue_id.return_value = entries
        mock_time_entry_repository.get_total_hours_by_issue.return_value = Decimal("5.0")

        use_case = GetTimeSummaryUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_issue.id)

        assert result.total_hours == Decimal("5.0")
        assert result.hours_by_user[str(user_id1)] == 3.5
        assert result.hours_by_user[str(user_id2)] == 1.5

    @pytest.mark.asyncio
    async def test_get_time_summary_no_entries(self, mock_time_entry_repository, test_issue):
        """Test getting time summary with no entries."""
        mock_time_entry_repository.get_by_issue_id.return_value = []
        mock_time_entry_repository.get_total_hours_by_issue.return_value = Decimal("0")

        use_case = GetTimeSummaryUseCase(mock_time_entry_repository)

        result = await use_case.execute(test_issue.id)

        assert result.total_hours == Decimal("0")
        assert len(result.hours_by_user) == 0
        assert len(result.hours_by_date_range) == 0
