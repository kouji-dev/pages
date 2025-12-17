"""Unit tests for WorkflowRepository implementation."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.workflow import Workflow, WorkflowStatus, WorkflowTransition
from src.infrastructure.database.models.workflow import (
    WorkflowModel,
    WorkflowStatusModel,
)
from src.infrastructure.database.repositories.workflow_repository import (
    SQLAlchemyWorkflowRepository,
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
def test_workflow(test_project_id):
    """Create a test workflow entity."""
    workflow = Workflow.create(
        project_id=test_project_id,
        name="Test Workflow",
        is_default=True,
    )

    # Add statuses
    status1 = WorkflowStatus.create(
        workflow_id=workflow.id,
        name="To Do",
        order=0,
        is_initial=True,
        is_final=False,
    )
    status2 = WorkflowStatus.create(
        workflow_id=workflow.id,
        name="Done",
        order=1,
        is_initial=False,
        is_final=True,
    )
    workflow.statuses = [status1, status2]

    # Add transition
    transition = WorkflowTransition.create(
        workflow_id=workflow.id,
        from_status_id=status1.id,
        to_status_id=status2.id,
        name="Complete",
    )
    workflow.transitions = [transition]

    return workflow


@pytest.mark.asyncio
async def test_create_workflow(mock_session, test_workflow):
    """Test creating a workflow."""
    # Setup mock to return workflow model
    workflow_model = WorkflowModel(
        id=test_workflow.id,
        project_id=test_workflow.project_id,
        name=test_workflow.name,
        is_default=test_workflow.is_default,
        created_at=test_workflow.created_at,
        updated_at=test_workflow.updated_at,
    )

    # Mock statuses and transitions
    status_model1 = WorkflowStatusModel(
        id=test_workflow.statuses[0].id,
        workflow_id=test_workflow.id,
        name=test_workflow.statuses[0].name,
        order=test_workflow.statuses[0].order,
        is_initial=test_workflow.statuses[0].is_initial,
        is_final=test_workflow.statuses[0].is_final,
        created_at=test_workflow.statuses[0].created_at,
        updated_at=test_workflow.statuses[0].updated_at,
    )
    status_model2 = WorkflowStatusModel(
        id=test_workflow.statuses[1].id,
        workflow_id=test_workflow.id,
        name=test_workflow.statuses[1].name,
        order=test_workflow.statuses[1].order,
        is_initial=test_workflow.statuses[1].is_initial,
        is_final=test_workflow.statuses[1].is_final,
        created_at=test_workflow.statuses[1].created_at,
        updated_at=test_workflow.statuses[1].updated_at,
    )
    workflow_model.statuses = [status_model1, status_model2]
    workflow_model.transitions = []

    # Mock the query result for _get_by_id call
    mock_result = create_mock_result(scalar_value=workflow_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyWorkflowRepository(mock_session)
    created = await repository.create(test_workflow)

    assert created is not None
    assert created.id == test_workflow.id
    assert created.name == test_workflow.name
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_found(mock_session, test_workflow):
    """Test getting workflow by ID when found."""
    workflow_model = WorkflowModel(
        id=test_workflow.id,
        project_id=test_workflow.project_id,
        name=test_workflow.name,
        is_default=test_workflow.is_default,
        created_at=test_workflow.created_at,
        updated_at=test_workflow.updated_at,
    )
    workflow_model.statuses = []
    workflow_model.transitions = []

    mock_result = create_mock_result(scalar_value=workflow_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyWorkflowRepository(mock_session)
    found = await repository.get_by_id(test_workflow.id)

    assert found is not None
    assert found.id == test_workflow.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_session):
    """Test getting workflow by ID when not found."""
    # Create a mock result that returns None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyWorkflowRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_by_project_id(mock_session, test_project_id, test_workflow):
    """Test getting workflows by project ID."""
    workflow_model = WorkflowModel(
        id=test_workflow.id,
        project_id=test_workflow.project_id,
        name=test_workflow.name,
        is_default=test_workflow.is_default,
        created_at=test_workflow.created_at,
        updated_at=test_workflow.updated_at,
    )
    workflow_model.statuses = []
    workflow_model.transitions = []

    mock_result = create_mock_result(scalars_list=[workflow_model])
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyWorkflowRepository(mock_session)
    workflows = await repository.get_by_project_id(test_project_id)

    assert len(workflows) == 1
    assert workflows[0].id == test_workflow.id


@pytest.mark.asyncio
async def test_update_workflow(mock_session, test_workflow):
    """Test updating a workflow."""
    workflow_model = WorkflowModel(
        id=test_workflow.id,
        project_id=test_workflow.project_id,
        name=test_workflow.name,
        is_default=test_workflow.is_default,
        created_at=test_workflow.created_at,
        updated_at=test_workflow.updated_at,
    )
    workflow_model.statuses = []
    workflow_model.transitions = []

    mock_result = create_mock_result(scalar_value=workflow_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyWorkflowRepository(mock_session)
    test_workflow.update_name("Updated Workflow")
    updated = await repository.update(test_workflow)

    assert updated is not None
    mock_session.flush.assert_called()


@pytest.mark.asyncio
async def test_delete_workflow(mock_session, test_workflow):
    """Test deleting a workflow."""
    workflow_model = WorkflowModel(
        id=test_workflow.id,
        project_id=test_workflow.project_id,
        name=test_workflow.name,
        is_default=test_workflow.is_default,
        created_at=test_workflow.created_at,
        updated_at=test_workflow.updated_at,
    )

    mock_result = create_mock_result(scalar_value=workflow_model)
    mock_session.execute = AsyncMock(return_value=mock_result)
    # delete is an async method in SQLAlchemy
    mock_session.delete = AsyncMock()

    repository = SQLAlchemyWorkflowRepository(mock_session)
    await repository.delete(test_workflow.id)

    mock_session.delete.assert_called_once_with(workflow_model)
