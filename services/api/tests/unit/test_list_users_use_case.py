"""Unit tests for list users use case."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.list_users import ListUsersUseCase
from src.domain.entities import User
from src.domain.value_objects import Email


class TestListUsersUseCase:
    """Tests for ListUsersUseCase."""

    @pytest.fixture
    def mock_session(self):
        """Get mock database session."""
        return MagicMock()

    @pytest.fixture
    def password_service(self):
        """Get password service for creating test users."""
        from src.infrastructure.security import BcryptPasswordService

        return BcryptPasswordService()

    @pytest.fixture
    def test_users(self, password_service):
        """Create test users."""
        from src.domain.value_objects import Password

        password = Password("TestPassword123!")
        hashed_password = password_service.hash(password)

        users = []
        for i in range(5):
            user = User.create(
                email=Email(f"user{i}@example.com"),
                password_hash=hashed_password,
                name=f"User {i}",
            )
            users.append(user)
        return users

    @pytest.mark.asyncio
    async def test_list_users_success(self, test_users, mock_session) -> None:
        """Test successfully listing users with pagination."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_all.return_value = test_users[:3]
        user_repository.count.return_value = 5

        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute
        result = await use_case.execute(page=1, limit=3)

        # Assert
        assert len(result.users) == 3
        assert result.total == 5
        assert result.page == 1
        assert result.limit == 3
        assert result.pages == 2
        user_repository.get_all.assert_called_once_with(skip=0, limit=3, include_deleted=False)

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, test_users, mock_session) -> None:
        """Test pagination works correctly."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_all.return_value = test_users[2:4]
        user_repository.count.return_value = 5

        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute - page 2
        result = await use_case.execute(page=2, limit=2)

        # Assert
        assert result.page == 2
        assert result.limit == 2
        assert result.pages == 3
        # Should skip 2 users (page 1 has users 0-1)
        user_repository.get_all.assert_called_once_with(skip=2, limit=2, include_deleted=False)

    @pytest.mark.asyncio
    async def test_list_users_with_search(self, test_users, mock_session) -> None:
        """Test listing users with search query."""
        # Setup
        user_repository = AsyncMock()
        user_repository.search.return_value = [test_users[0]]

        use_case = ListUsersUseCase(user_repository, mock_session)

        # Mock the _count_search_results method
        use_case._count_search_results = AsyncMock(return_value=1)

        # Execute
        result = await use_case.execute(page=1, limit=20, search="User 0")

        # Assert
        assert len(result.users) == 1
        assert result.total == 1
        user_repository.search.assert_called_once_with(query="User 0", skip=0, limit=20)

    @pytest.mark.asyncio
    async def test_list_users_invalid_page(self, test_users, mock_session) -> None:
        """Test that invalid page number raises error."""
        # Setup
        user_repository = AsyncMock()
        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute & Assert
        with pytest.raises(ValueError, match="Page must be >= 1"):
            await use_case.execute(page=0, limit=20)

    @pytest.mark.asyncio
    async def test_list_users_invalid_limit(self, test_users, mock_session) -> None:
        """Test that invalid limit raises error."""
        # Setup
        user_repository = AsyncMock()
        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute & Assert
        with pytest.raises(ValueError, match="Limit must be >= 1"):
            await use_case.execute(page=1, limit=0)

    @pytest.mark.asyncio
    async def test_list_users_limit_exceeds_max(self, test_users, mock_session) -> None:
        """Test that limit exceeding max is capped."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_all.return_value = test_users
        user_repository.count.return_value = 5

        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute with limit > MAX_LIMIT
        result = await use_case.execute(page=1, limit=200)

        # Assert - limit should be capped at MAX_LIMIT
        assert result.limit == ListUsersUseCase.MAX_LIMIT
        user_repository.get_all.assert_called_once_with(
            skip=0, limit=ListUsersUseCase.MAX_LIMIT, include_deleted=False
        )

    @pytest.mark.asyncio
    async def test_list_users_empty_result(self, mock_session) -> None:
        """Test listing users when no users exist."""
        # Setup
        user_repository = AsyncMock()
        user_repository.get_all.return_value = []
        user_repository.count.return_value = 0

        use_case = ListUsersUseCase(user_repository, mock_session)

        # Execute
        result = await use_case.execute(page=1, limit=20)

        # Assert
        assert len(result.users) == 0
        assert result.total == 0
        assert result.pages == 0
