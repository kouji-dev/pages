"""Unit tests for custom field use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.custom_field import CustomFieldRequest
from src.application.use_cases.custom_field import (
    CreateCustomFieldUseCase,
    DeleteCustomFieldUseCase,
    GetCustomFieldUseCase,
    ListCustomFieldsUseCase,
    UpdateCustomFieldUseCase,
)
from src.domain.entities import Project
from src.domain.entities.custom_field import CustomField
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_custom_field_repository():
    """Mock custom field repository."""
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
def test_custom_field(test_project):
    """Create a test custom field."""
    return CustomField.create(
        project_id=test_project.id,
        name="Priority Level",
        type="select",
        is_required=False,
        options=["Low", "Medium", "High"],
    )


class TestCreateCustomFieldUseCase:
    """Tests for CreateCustomFieldUseCase."""

    @pytest.mark.asyncio
    async def test_create_custom_field_success(
        self,
        mock_custom_field_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful custom field creation."""
        request = CustomFieldRequest(
            name="Priority Level",
            type="select",
            is_required=False,
            options=["Low", "Medium", "High"],
        )

        mock_project_repository.get_by_id.return_value = test_project

        created_field = CustomField.create(
            project_id=test_project.id,
            name=request.name,
            type=request.type,
            is_required=request.is_required,
            options=request.options,
        )

        mock_custom_field_repository.create.return_value = created_field

        use_case = CreateCustomFieldUseCase(mock_custom_field_repository, mock_project_repository)

        result = await use_case.execute(test_project.id, request)

        assert result.name == "Priority Level"
        assert result.type == "select"
        assert result.options == ["Low", "Medium", "High"]
        mock_custom_field_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_custom_field_project_not_found(
        self,
        mock_custom_field_repository,
        mock_project_repository,
    ):
        """Test custom field creation with non-existent project."""
        request = CustomFieldRequest(name="Test Field", type="text")
        project_id = uuid4()

        mock_project_repository.get_by_id.return_value = None

        use_case = CreateCustomFieldUseCase(mock_custom_field_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(project_id, request)


class TestGetCustomFieldUseCase:
    """Tests for GetCustomFieldUseCase."""

    @pytest.mark.asyncio
    async def test_get_custom_field_success(self, mock_custom_field_repository, test_custom_field):
        """Test successfully getting a custom field."""
        mock_custom_field_repository.get_by_id.return_value = test_custom_field

        use_case = GetCustomFieldUseCase(mock_custom_field_repository)

        result = await use_case.execute(test_custom_field.id)

        assert result.id == test_custom_field.id
        assert result.name == test_custom_field.name
        mock_custom_field_repository.get_by_id.assert_called_once_with(test_custom_field.id)

    @pytest.mark.asyncio
    async def test_get_custom_field_not_found(self, mock_custom_field_repository):
        """Test getting non-existent custom field."""
        field_id = uuid4()
        mock_custom_field_repository.get_by_id.return_value = None

        use_case = GetCustomFieldUseCase(mock_custom_field_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(field_id)


class TestListCustomFieldsUseCase:
    """Tests for ListCustomFieldsUseCase."""

    @pytest.mark.asyncio
    async def test_list_custom_fields_success(
        self, mock_custom_field_repository, test_project, test_custom_field
    ):
        """Test successfully listing custom fields."""
        fields = [test_custom_field]
        mock_custom_field_repository.get_by_project_id.return_value = fields

        use_case = ListCustomFieldsUseCase(mock_custom_field_repository)

        result = await use_case.execute(test_project.id)

        assert result.total == 1
        assert len(result.fields) == 1
        assert result.fields[0].id == test_custom_field.id


class TestUpdateCustomFieldUseCase:
    """Tests for UpdateCustomFieldUseCase."""

    @pytest.mark.asyncio
    async def test_update_custom_field_success(
        self, mock_custom_field_repository, test_custom_field
    ):
        """Test successfully updating a custom field."""
        request = CustomFieldRequest(
            name="Updated Field",
            type=test_custom_field.type,
            is_required=test_custom_field.is_required,
            options=test_custom_field.options,
        )

        updated_field = CustomField.create(
            project_id=test_custom_field.project_id,
            name=request.name,
            type=request.type,
            is_required=request.is_required,
            options=request.options,
        )

        mock_custom_field_repository.get_by_id.return_value = test_custom_field
        mock_custom_field_repository.update.return_value = updated_field

        use_case = UpdateCustomFieldUseCase(mock_custom_field_repository)

        result = await use_case.execute(test_custom_field.id, request)

        assert result.name == "Updated Field"
        mock_custom_field_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_custom_field_not_found(self, mock_custom_field_repository):
        """Test updating non-existent custom field."""
        field_id = uuid4()
        request = CustomFieldRequest(name="Updated Field", type="text")

        mock_custom_field_repository.get_by_id.return_value = None

        use_case = UpdateCustomFieldUseCase(mock_custom_field_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(field_id, request)


class TestDeleteCustomFieldUseCase:
    """Tests for DeleteCustomFieldUseCase."""

    @pytest.mark.asyncio
    async def test_delete_custom_field_success(
        self, mock_custom_field_repository, test_custom_field
    ):
        """Test successfully deleting a custom field."""
        mock_custom_field_repository.get_by_id.return_value = test_custom_field
        mock_custom_field_repository.delete.return_value = None

        use_case = DeleteCustomFieldUseCase(mock_custom_field_repository)

        await use_case.execute(test_custom_field.id)

        mock_custom_field_repository.delete.assert_called_once_with(test_custom_field.id)

    @pytest.mark.asyncio
    async def test_delete_custom_field_not_found(self, mock_custom_field_repository):
        """Test deleting non-existent custom field."""
        field_id = uuid4()
        mock_custom_field_repository.get_by_id.return_value = None

        use_case = DeleteCustomFieldUseCase(mock_custom_field_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(field_id)
