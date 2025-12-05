"""Tests for domain entities."""

import pytest
from datetime import datetime
from uuid import uuid4

from src.domain.entities import User
from src.domain.value_objects import Email, HashedPassword
from src.infrastructure.security import BcryptPasswordService


class TestUser:
    """Tests for User entity."""

    @pytest.fixture
    def password_service(self) -> BcryptPasswordService:
        """Get password service."""
        return BcryptPasswordService()

    @pytest.fixture
    def valid_email(self) -> Email:
        """Create valid email."""
        return Email("test@example.com")

    @pytest.fixture
    def hashed_password(self, password_service: BcryptPasswordService) -> HashedPassword:
        """Create hashed password."""
        from src.domain.value_objects import Password
        return password_service.hash(Password("SecurePass123!"))

    def test_create_user(self, valid_email: Email, hashed_password: HashedPassword) -> None:
        """Test creating a new user."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        assert user.id is not None
        assert user.email == valid_email
        assert user.password_hash == hashed_password
        assert user.name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.avatar_url is None
        assert user.deleted_at is None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_with_avatar(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test creating user with avatar."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
            avatar_url="https://example.com/avatar.png",
        )

        assert user.avatar_url == "https://example.com/avatar.png"

    def test_user_name_validation_empty(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user name cannot be empty."""
        with pytest.raises(ValueError) as exc_info:
            User.create(
                email=valid_email,
                password_hash=hashed_password,
                name="",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_user_name_validation_whitespace(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user name cannot be only whitespace."""
        with pytest.raises(ValueError):
            User.create(
                email=valid_email,
                password_hash=hashed_password,
                name="   ",
            )

    def test_user_name_validation_too_long(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user name cannot exceed 100 characters."""
        with pytest.raises(ValueError) as exc_info:
            User.create(
                email=valid_email,
                password_hash=hashed_password,
                name="A" * 101,
            )
        assert "100" in str(exc_info.value)

    def test_user_name_is_trimmed(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user name whitespace is trimmed."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="  Test User  ",
        )
        assert user.name == "Test User"

    def test_update_name(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test updating user name."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Original Name",
        )
        original_updated_at = user.updated_at

        user.update_name("New Name")

        assert user.name == "New Name"
        assert user.updated_at >= original_updated_at

    def test_update_name_empty_raises_error(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test updating name to empty raises error."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        with pytest.raises(ValueError):
            user.update_name("")

    def test_update_avatar(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test updating user avatar."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        user.update_avatar("https://example.com/new-avatar.png")

        assert user.avatar_url == "https://example.com/new-avatar.png"

    def test_update_avatar_to_none(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test removing user avatar."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
            avatar_url="https://example.com/avatar.png",
        )

        user.update_avatar(None)

        assert user.avatar_url is None

    def test_verify_user(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test verifying user."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        assert user.is_verified is False
        user.verify()
        assert user.is_verified is True

    def test_deactivate_user(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test deactivating user (soft delete)."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        assert user.is_active is True
        assert user.is_deleted is False

        user.deactivate()

        assert user.is_active is False
        assert user.is_deleted is True
        assert user.deleted_at is not None

    def test_deactivate_already_deactivated_user(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test deactivating already deactivated user does nothing."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )
        user.deactivate()
        deleted_at = user.deleted_at

        user.deactivate()  # Should not change anything

        assert user.deleted_at == deleted_at

    def test_reactivate_user(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test reactivating user."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )
        user.deactivate()

        user.reactivate()

        assert user.is_active is True
        assert user.is_deleted is False
        assert user.deleted_at is None

    def test_user_equality(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user equality based on ID."""
        user1 = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )
        user2 = User(
            id=user1.id,
            email=Email("other@example.com"),
            password_hash=hashed_password,
            name="Other Name",
        )

        assert user1 == user2  # Same ID

    def test_user_hash(
        self, valid_email: Email, hashed_password: HashedPassword
    ) -> None:
        """Test user can be used in sets."""
        user = User.create(
            email=valid_email,
            password_hash=hashed_password,
            name="Test User",
        )

        user_set = {user}
        assert len(user_set) == 1

