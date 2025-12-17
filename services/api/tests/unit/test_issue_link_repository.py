"""Unit tests for IssueLinkRepository implementation."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.issue_link import IssueLink
from src.infrastructure.database.models.issue_link import IssueLinkModel
from src.infrastructure.database.repositories.issue_link_repository import (
    SQLAlchemyIssueLinkRepository,
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
def test_issue_link():
    """Create a test issue link entity."""
    return IssueLink.create(
        source_issue_id=uuid4(),
        target_issue_id=uuid4(),
        link_type="blocks",
    )


@pytest.mark.asyncio
async def test_create_issue_link(mock_session, test_issue_link):
    """Test creating an issue link."""
    link_model = IssueLinkModel(
        id=test_issue_link.id,
        source_issue_id=test_issue_link.source_issue_id,
        target_issue_id=test_issue_link.target_issue_id,
        link_type=test_issue_link.link_type,
        created_at=test_issue_link.created_at,
        updated_at=test_issue_link.updated_at,
    )

    mock_result = create_mock_result(scalar_value=link_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyIssueLinkRepository(mock_session)
    created = await repository.create(test_issue_link)

    assert created is not None
    assert created.id == test_issue_link.id
    mock_session.add.assert_called()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_issue_link_by_id_found(mock_session, test_issue_link):
    """Test getting issue link by ID when found."""
    link_model = IssueLinkModel(
        id=test_issue_link.id,
        source_issue_id=test_issue_link.source_issue_id,
        target_issue_id=test_issue_link.target_issue_id,
        link_type=test_issue_link.link_type,
        created_at=test_issue_link.created_at,
        updated_at=test_issue_link.updated_at,
    )

    mock_result = create_mock_result(scalar_value=link_model)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyIssueLinkRepository(mock_session)
    found = await repository.get_by_id(test_issue_link.id)

    assert found is not None
    assert found.id == test_issue_link.id


@pytest.mark.asyncio
async def test_get_issue_link_by_id_not_found(mock_session):
    """Test getting issue link by ID when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repository = SQLAlchemyIssueLinkRepository(mock_session)
    found = await repository.get_by_id(uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_issue_links_by_issue_id(mock_session, test_issue_link):
    """Test getting issue links by issue ID."""
    link_model = IssueLinkModel(
        id=test_issue_link.id,
        source_issue_id=test_issue_link.source_issue_id,
        target_issue_id=test_issue_link.target_issue_id,
        link_type=test_issue_link.link_type,
        created_at=test_issue_link.created_at,
        updated_at=test_issue_link.updated_at,
    )

    # get_by_issue_id calls both get_outgoing_links and get_incoming_links
    mock_result_outgoing = create_mock_result(scalars_list=[link_model])
    mock_result_incoming = create_mock_result(scalars_list=[])
    mock_session.execute = AsyncMock(side_effect=[mock_result_outgoing, mock_result_incoming])

    repository = SQLAlchemyIssueLinkRepository(mock_session)
    links = await repository.get_by_issue_id(test_issue_link.source_issue_id)

    assert len(links) == 1
    assert links[0].id == test_issue_link.id
