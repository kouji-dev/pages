"""Unit tests for macro use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.macro import (
    CreateMacroRequest,
    ExecuteMacroRequest,
    UpdateMacroRequest,
)
from src.application.use_cases.macro import (
    CreateMacroUseCase,
    DeleteMacroUseCase,
    ExecuteMacroUseCase,
    GetMacroUseCase,
    ListMacrosUseCase,
    UpdateMacroUseCase,
)
from src.domain.entities import Macro
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_macro_repository():
    """Mock macro repository."""
    return AsyncMock()


@pytest.fixture
def test_macro():
    """Create a test macro."""
    return Macro.create(
        name="Test Macro",
        code="<div>{{content}}</div>",
        macro_type="info_panel",
    )


class TestCreateMacroUseCase:
    """Tests for CreateMacroUseCase."""

    @pytest.mark.asyncio
    async def test_create_macro_success(self, mock_macro_repository, test_macro):
        """Test successful macro creation."""
        mock_macro_repository.get_by_name.return_value = None
        mock_macro_repository.create.return_value = test_macro

        request = CreateMacroRequest(
            name="Test Macro",
            code="<div>{{content}}</div>",
            macro_type="info_panel",
        )

        use_case = CreateMacroUseCase(mock_macro_repository)
        result = await use_case.execute(request)

        assert result.name == "Test Macro"
        assert result.macro_type == "info_panel"
        mock_macro_repository.get_by_name.assert_called_once()
        mock_macro_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_macro_name_exists(self, mock_macro_repository, test_macro):
        """Test macro creation when name already exists."""
        mock_macro_repository.get_by_name.return_value = test_macro

        request = CreateMacroRequest(
            name="Test Macro",
            code="<div>{{content}}</div>",
            macro_type="info_panel",
        )

        use_case = CreateMacroUseCase(mock_macro_repository)

        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(request)


class TestListMacrosUseCase:
    """Tests for ListMacrosUseCase."""

    @pytest.mark.asyncio
    async def test_list_macros_success(self, mock_macro_repository, test_macro):
        """Test successful macro listing."""
        mock_macro_repository.get_all.return_value = [test_macro]
        mock_macro_repository.count.return_value = 1

        use_case = ListMacrosUseCase(mock_macro_repository)
        result = await use_case.execute(page=1, limit=20)

        assert result.total == 1
        assert len(result.macros) == 1
        assert result.macros[0].name == "Test Macro"


class TestGetMacroUseCase:
    """Tests for GetMacroUseCase."""

    @pytest.mark.asyncio
    async def test_get_macro_success(self, mock_macro_repository, test_macro):
        """Test successful macro retrieval."""
        mock_macro_repository.get_by_id.return_value = test_macro

        use_case = GetMacroUseCase(mock_macro_repository)
        result = await use_case.execute(str(test_macro.id))

        assert result.name == "Test Macro"

    @pytest.mark.asyncio
    async def test_get_macro_not_found(self, mock_macro_repository):
        """Test macro retrieval when macro not found."""
        mock_macro_repository.get_by_id.return_value = None

        use_case = GetMacroUseCase(mock_macro_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdateMacroUseCase:
    """Tests for UpdateMacroUseCase."""

    @pytest.mark.asyncio
    async def test_update_macro_success(self, mock_macro_repository, test_macro):
        """Test successful macro update."""
        mock_macro_repository.get_by_id.return_value = test_macro
        mock_macro_repository.update.return_value = test_macro

        request = UpdateMacroRequest(name="Updated Macro")

        use_case = UpdateMacroUseCase(mock_macro_repository)
        result = await use_case.execute(str(test_macro.id), request)

        assert result.name == "Updated Macro"

    @pytest.mark.asyncio
    async def test_update_macro_not_found(self, mock_macro_repository):
        """Test macro update when macro not found."""
        mock_macro_repository.get_by_id.return_value = None

        request = UpdateMacroRequest(name="Updated Macro")

        use_case = UpdateMacroUseCase(mock_macro_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)


class TestDeleteMacroUseCase:
    """Tests for DeleteMacroUseCase."""

    @pytest.mark.asyncio
    async def test_delete_macro_success(self, mock_macro_repository, test_macro):
        """Test successful macro deletion."""
        mock_macro_repository.get_by_id.return_value = test_macro

        use_case = DeleteMacroUseCase(mock_macro_repository)
        await use_case.execute(str(test_macro.id))

        mock_macro_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_macro_not_found(self, mock_macro_repository):
        """Test macro deletion when macro not found."""
        mock_macro_repository.get_by_id.return_value = None

        use_case = DeleteMacroUseCase(mock_macro_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestExecuteMacroUseCase:
    """Tests for ExecuteMacroUseCase."""

    @pytest.mark.asyncio
    async def test_execute_macro_success(self, mock_macro_repository, test_macro):
        """Test successful macro execution."""
        mock_macro_repository.get_by_name.return_value = test_macro

        request = ExecuteMacroRequest(macro_name="Test Macro", config={"content": "Hello"})

        use_case = ExecuteMacroUseCase(mock_macro_repository)
        result = await use_case.execute(request)

        assert result.macro_name == "Test Macro"
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_execute_macro_not_found(self, mock_macro_repository):
        """Test macro execution when macro not found."""
        mock_macro_repository.get_by_name.return_value = None

        request = ExecuteMacroRequest(macro_name="Non-existent", config={})

        use_case = ExecuteMacroUseCase(mock_macro_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request)
