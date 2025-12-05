"""Tests for Role value object."""

import pytest

from src.domain.value_objects import Role


class TestRole:
    """Tests for Role value object."""

    def test_role_values(self) -> None:
        """Test role enum values."""
        assert Role.ADMIN.value == "admin"
        assert Role.MEMBER.value == "member"
        assert Role.VIEWER.value == "viewer"

    def test_role_string_representation(self) -> None:
        """Test role string representation."""
        assert str(Role.ADMIN) == "admin"
        assert str(Role.MEMBER) == "member"
        assert str(Role.VIEWER) == "viewer"

    def test_role_is_valid_valid_values(self) -> None:
        """Test is_valid with valid role values."""
        assert Role.is_valid("admin") is True
        assert Role.is_valid("member") is True
        assert Role.is_valid("viewer") is True

    def test_role_is_valid_invalid_values(self) -> None:
        """Test is_valid with invalid role values."""
        assert Role.is_valid("invalid") is False
        assert Role.is_valid("") is False
        assert Role.is_valid("ADMIN") is False  # Case sensitive
        assert Role.is_valid("Admin") is False  # Case sensitive

    def test_can_manage_members(self) -> None:
        """Test can_manage_members permission check."""
        assert Role.ADMIN.can_manage_members() is True
        assert Role.MEMBER.can_manage_members() is False
        assert Role.VIEWER.can_manage_members() is False

    def test_can_edit_content(self) -> None:
        """Test can_edit_content permission check."""
        assert Role.ADMIN.can_edit_content() is True
        assert Role.MEMBER.can_edit_content() is True
        assert Role.VIEWER.can_edit_content() is False

    def test_can_view(self) -> None:
        """Test can_view permission check."""
        assert Role.ADMIN.can_view() is True
        assert Role.MEMBER.can_view() is True
        assert Role.VIEWER.can_view() is True

    def test_can_delete(self) -> None:
        """Test can_delete permission check."""
        assert Role.ADMIN.can_delete() is True
        assert Role.MEMBER.can_delete() is False
        assert Role.VIEWER.can_delete() is False

    def test_role_comparison(self) -> None:
        """Test role comparison."""
        assert Role.ADMIN == Role.ADMIN
        assert Role.ADMIN != Role.MEMBER
        assert Role.ADMIN != Role.VIEWER

    def test_role_from_string(self) -> None:
        """Test creating role from string value."""
        assert Role("admin") == Role.ADMIN
        assert Role("member") == Role.MEMBER
        assert Role("viewer") == Role.VIEWER

    def test_role_from_invalid_string_raises_error(self) -> None:
        """Test creating role from invalid string raises ValueError."""
        with pytest.raises(ValueError):
            Role("invalid")
