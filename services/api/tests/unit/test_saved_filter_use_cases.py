"""Unit tests for saved filter use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.saved_filter import (
    CreateSavedFilterRequest,
    UpdateSavedFilterRequest,
)
from src.application.use_cases.saved_filter import (
    CreateSavedFilterUseCase,
    DeleteSavedFilterUseCase,
    GetSavedFilterUseCase,
    ListSavedFiltersUseCase,
    UpdateSavedFilterUseCase,
)
from src.domain.entities import Project, SavedFilter
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_saved_filter_repository():
    """Mock saved filter repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
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
def test_saved_filter(test_project):
    """Create a test saved filter."""
    return SavedFilter.create(
        user_id=uuid4(),
        name="My Filter",
        filter_criteria={"status": "todo", "priority": "high"},
        project_id=test_project.id,
    )


class TestCreateSavedFilterUseCase:
    """Tests for CreateSavedFilterUseCase."""

    @pytest.mark.asyncio
    async def test_create_saved_filter_success(
        self,
        mock_saved_filter_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful saved filter creation."""
        user_id = uuid4()
        request = CreateSavedFilterRequest(
            name="My Filter",
            project_id=test_project.id,
            filter_criteria={"status": "todo", "priority": "high"},
        )

        mock_project_repository.get_by_id.return_value = test_project

        created_filter = SavedFilter.create(
            user_id=user_id,
            name=request.name,
            filter_criteria=request.filter_criteria,
            project_id=request.project_id,
        )

        mock_saved_filter_repository.create.return_value = created_filter

        use_case = CreateSavedFilterUseCase(mock_saved_filter_repository, mock_project_repository)

        result = await use_case.execute(user_id, request)

        assert result.name == "My Filter"
        assert result.filter_criteria == {"status": "todo", "priority": "high"}
        mock_saved_filter_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_saved_filter_project_not_found(
        self,
        mock_saved_filter_repository,
        mock_project_repository,
    ):
        """Test saved filter creation with non-existent project."""
        user_id = uuid4()
        request = CreateSavedFilterRequest(name="My Filter", project_id=uuid4(), filter_criteria={})

        mock_project_repository.get_by_id.return_value = None

        use_case = CreateSavedFilterUseCase(mock_saved_filter_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(user_id, request)


class TestGetSavedFilterUseCase:
    """Tests for GetSavedFilterUseCase."""

    @pytest.mark.asyncio
    async def test_get_saved_filter_success(self, mock_saved_filter_repository, test_saved_filter):
        """Test successfully getting a saved filter."""
        mock_saved_filter_repository.get_by_id.return_value = test_saved_filter

        use_case = GetSavedFilterUseCase(mock_saved_filter_repository)

        result = await use_case.execute(test_saved_filter.id)

        assert result.id == test_saved_filter.id
        assert result.name == test_saved_filter.name
        mock_saved_filter_repository.get_by_id.assert_called_once_with(test_saved_filter.id)

    @pytest.mark.asyncio
    async def test_get_saved_filter_not_found(self, mock_saved_filter_repository):
        """Test getting non-existent saved filter."""
        filter_id = uuid4()
        mock_saved_filter_repository.get_by_id.return_value = None

        use_case = GetSavedFilterUseCase(mock_saved_filter_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(filter_id)


class TestListSavedFiltersUseCase:
    """Tests for ListSavedFiltersUseCase."""

    @pytest.mark.asyncio
    async def test_list_saved_filters_success(
        self, mock_saved_filter_repository, test_saved_filter
    ):
        """Test successfully listing saved filters."""
        filters = [test_saved_filter]
        mock_saved_filter_repository.get_by_user_id.return_value = filters

        use_case = ListSavedFiltersUseCase(mock_saved_filter_repository)

        result = await use_case.execute(test_saved_filter.user_id, None)

        assert result.total == 1
        assert len(result.filters) == 1
        assert result.filters[0].id == test_saved_filter.id


class TestUpdateSavedFilterUseCase:
    """Tests for UpdateSavedFilterUseCase."""

    @pytest.mark.asyncio
    async def test_update_saved_filter_success(
        self, mock_saved_filter_repository, test_saved_filter
    ):
        """Test successfully updating a saved filter."""
        request = UpdateSavedFilterRequest(name="Updated Filter")

        updated_filter = SavedFilter.create(
            user_id=test_saved_filter.user_id,
            name=request.name,
            filter_criteria=test_saved_filter.filter_criteria,
            project_id=test_saved_filter.project_id,
        )

        mock_saved_filter_repository.get_by_id.return_value = test_saved_filter
        mock_saved_filter_repository.update.return_value = updated_filter

        use_case = UpdateSavedFilterUseCase(mock_saved_filter_repository)

        result = await use_case.execute(test_saved_filter.id, request)

        assert result.name == "Updated Filter"
        mock_saved_filter_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_saved_filter_not_found(self, mock_saved_filter_repository):
        """Test updating non-existent saved filter."""
        filter_id = uuid4()
        request = UpdateSavedFilterRequest(name="Updated Filter")

        mock_saved_filter_repository.get_by_id.return_value = None

        use_case = UpdateSavedFilterUseCase(mock_saved_filter_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(filter_id, request)


class TestDeleteSavedFilterUseCase:
    """Tests for DeleteSavedFilterUseCase."""

    @pytest.mark.asyncio
    async def test_delete_saved_filter_success(
        self, mock_saved_filter_repository, test_saved_filter
    ):
        """Test successfully deleting a saved filter."""
        mock_saved_filter_repository.get_by_id.return_value = test_saved_filter
        mock_saved_filter_repository.delete.return_value = None

        use_case = DeleteSavedFilterUseCase(mock_saved_filter_repository)

        await use_case.execute(test_saved_filter.id)

        mock_saved_filter_repository.delete.assert_called_once_with(test_saved_filter.id)

    @pytest.mark.asyncio
    async def test_delete_saved_filter_not_found(self, mock_saved_filter_repository):
        """Test deleting non-existent saved filter."""
        filter_id = uuid4()
        mock_saved_filter_repository.get_by_id.return_value = None

        use_case = DeleteSavedFilterUseCase(mock_saved_filter_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(filter_id)
