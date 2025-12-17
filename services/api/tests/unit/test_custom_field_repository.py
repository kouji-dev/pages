"""Unit tests for CustomFieldRepository implementation."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.custom_field import CustomField, CustomFieldValue
from src.infrastructure.database.models.custom_field import (
    CustomFieldModel,
    CustomFieldValueModel,
)
from src.infrastructure.database.repositories.custom_field_repository import (
    SQLAlchemyCustomFieldRepository,
    SQLAlchemyCustomFieldValueRepository,
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
def test_custom_field(test_project_id):
    """Create a test custom field entity."""
    return CustomField.create(
        project_id=test_project_id,
        name="Test Field",
        type="text",
        is_required=False,
    )


@pytest.fixture
def test_custom_field_value(test_custom_field):
    """Create a test custom field value entity."""
    issue_id = uuid4()
    return CustomFieldValue.create(
        custom_field_id=test_custom_field.id,
        issue_id=issue_id,
        value="Test Value",
    )


@pytest.mark.asyncio
async def test_create_custom_field(mock_session, test_custom_field):
    """Test creating a custom field."""
    field_model = CustomFieldModel(
        id=test_custom_field.id,
        project_id=test_custom_field.project_id,
        name=test_custom_field.name,
        type=test_custom_field.type,
        is_required=test_custom_field.is_required,
        default_value=test_custom_field.default_value,
        created_at=test_custom_field.created_at,
        updated_at=test_custom_field.updated_at,
    )

    mock_result = create_mock_result(scalar_value=field_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldRepository(mock_session)
    created = await repository.create(test_custom_field)

    assert created is not None
    assert created.id == test_custom_field.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_custom_field_by_id_found(mock_session, test_custom_field):
    """Test getting custom field by ID when found."""
    field_model = CustomFieldModel(
        id=test_custom_field.id,
        project_id=test_custom_field.project_id,
        name=test_custom_field.name,
        type=test_custom_field.type,
        is_required=test_custom_field.is_required,
        default_value=test_custom_field.default_value,
        created_at=test_custom_field.created_at,
        updated_at=test_custom_field.updated_at,
    )

    mock_result = create_mock_result(scalar_value=field_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldRepository(mock_session)
    found = await repository.get_by_id(test_custom_field.id)

    assert found is not None
    assert found.id == test_custom_field.id


@pytest.mark.asyncio
async def test_get_custom_field_by_id_not_found(mock_session):
    """Test getting custom field by ID when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_custom_fields_by_project_id(mock_session, test_project_id, test_custom_field):
    """Test getting custom fields by project ID."""
    field_model = CustomFieldModel(
        id=test_custom_field.id,
        project_id=test_custom_field.project_id,
        name=test_custom_field.name,
        type=test_custom_field.type,
        is_required=test_custom_field.is_required,
        default_value=test_custom_field.default_value,
        created_at=test_custom_field.created_at,
        updated_at=test_custom_field.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[field_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldRepository(mock_session)
    fields = await repository.get_by_project_id(test_project_id)

    assert len(fields) == 1
    assert fields[0].id == test_custom_field.id


@pytest.mark.asyncio
async def test_create_custom_field_value(mock_session, test_custom_field_value):
    """Test creating a custom field value."""
    value_model = CustomFieldValueModel(
        id=test_custom_field_value.id,
        custom_field_id=test_custom_field_value.custom_field_id,
        issue_id=test_custom_field_value.issue_id,
        value=test_custom_field_value.value,
        created_at=test_custom_field_value.created_at,
        updated_at=test_custom_field_value.updated_at,
    )

    mock_result = create_mock_result(scalar_value=value_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldValueRepository(mock_session)
    created = await repository.create(test_custom_field_value)

    assert created is not None
    assert created.id == test_custom_field_value.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_custom_field_values_by_issue_id(mock_session, test_custom_field_value):
    """Test getting custom field values by issue ID."""
    value_model = CustomFieldValueModel(
        id=test_custom_field_value.id,
        custom_field_id=test_custom_field_value.custom_field_id,
        issue_id=test_custom_field_value.issue_id,
        value=test_custom_field_value.value,
        created_at=test_custom_field_value.created_at,
        updated_at=test_custom_field_value.updated_at,
    )

    mock_result = create_mock_result(scalars_list=[value_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyCustomFieldValueRepository(mock_session)
    values = await repository.get_by_issue_id(test_custom_field_value.issue_id)

    assert len(values) == 1
    assert values[0].id == test_custom_field_value.id
