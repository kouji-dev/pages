"""Tests for domain value objects."""

import pytest

from src.domain.exceptions import ValidationException
from src.domain.value_objects import Email, Password, HashedPassword


class TestEmail:
    """Tests for Email value object."""

    def test_create_valid_email(self) -> None:
        """Test creating a valid email."""
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_email_is_normalized(self) -> None:
        """Test email is normalized to lowercase."""
        email = Email("Test@EXAMPLE.COM")
        assert str(email) == "test@example.com"

    def test_email_is_trimmed(self) -> None:
        """Test email whitespace is trimmed."""
        email = Email("  test@example.com  ")
        assert str(email) == "test@example.com"

    def test_empty_email_raises_error(self) -> None:
        """Test empty email raises validation error."""
        with pytest.raises(ValidationException) as exc_info:
            Email("")
        assert "empty" in exc_info.value.message.lower()

    def test_invalid_email_format_raises_error(self) -> None:
        """Test invalid email format raises validation error."""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "test@.com",
        ]
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationException):
                Email(invalid_email)

    def test_email_too_long_raises_error(self) -> None:
        """Test email too long raises validation error."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationException) as exc_info:
            Email(long_email)
        assert "long" in exc_info.value.message.lower()

    def test_email_equality(self) -> None:
        """Test email equality comparison."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3
        assert email1 == "test@example.com"

    def test_email_domain_property(self) -> None:
        """Test email domain property."""
        email = Email("test@example.com")
        assert email.domain == "example.com"

    def test_email_local_part_property(self) -> None:
        """Test email local_part property."""
        email = Email("test@example.com")
        assert email.local_part == "test"

    def test_email_is_hashable(self) -> None:
        """Test email can be used in sets and as dict keys."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        
        email_set = {email1, email2}
        assert len(email_set) == 1


class TestPassword:
    """Tests for Password value object."""

    def test_create_valid_password(self) -> None:
        """Test creating a valid password."""
        password = Password("SecurePass123!")
        assert password.value == "SecurePass123!"

    def test_password_str_is_masked(self) -> None:
        """Test password string representation is masked."""
        password = Password("SecurePass123!")
        assert str(password) == "********"
        assert "SecurePass123" not in repr(password)

    def test_empty_password_raises_error(self) -> None:
        """Test empty password raises validation error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("")
        assert "empty" in exc_info.value.message.lower()

    def test_short_password_raises_error(self) -> None:
        """Test short password raises validation error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("Short1!")
        assert "8" in exc_info.value.message

    def test_long_password_raises_error(self) -> None:
        """Test password exceeding max length raises error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("A" * 129 + "a1!")
        assert "128" in exc_info.value.message

    def test_password_without_uppercase_raises_error(self) -> None:
        """Test password without uppercase raises error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("lowercase123!")
        assert "uppercase" in exc_info.value.message.lower()

    def test_password_without_lowercase_raises_error(self) -> None:
        """Test password without lowercase raises error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("UPPERCASE123!")
        assert "lowercase" in exc_info.value.message.lower()

    def test_password_without_digit_raises_error(self) -> None:
        """Test password without digit raises error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("NoDigits!!")
        assert "digit" in exc_info.value.message.lower()

    def test_password_without_special_char_raises_error(self) -> None:
        """Test password without special character raises error."""
        with pytest.raises(ValidationException) as exc_info:
            Password("NoSpecial123")
        assert "special" in exc_info.value.message.lower()

    def test_password_strength_weak(self) -> None:
        """Test weak password strength."""
        password = Password("Weak123!")
        assert password.strength == "weak"

    def test_password_strength_medium(self) -> None:
        """Test medium password strength."""
        password = Password("Medium123!@")
        assert password.strength == "medium"

    def test_password_strength_strong(self) -> None:
        """Test strong password strength."""
        password = Password("VeryStr0ng!@#Pass")
        assert password.strength == "strong"


class TestHashedPassword:
    """Tests for HashedPassword value object."""

    def test_create_valid_bcrypt_hash(self) -> None:
        """Test creating with valid bcrypt hash."""
        # Valid bcrypt hash format
        bcrypt_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        hashed = HashedPassword(bcrypt_hash)
        assert hashed.value == bcrypt_hash

    def test_create_valid_argon2_hash(self) -> None:
        """Test creating with valid argon2 hash."""
        # Valid argon2 hash format
        argon2_hash = "$argon2id$v=19$m=65536,t=3,p=4$somesalt$somehash"
        hashed = HashedPassword(argon2_hash)
        assert hashed.value == argon2_hash

    def test_empty_hash_raises_error(self) -> None:
        """Test empty hash raises validation error."""
        with pytest.raises(ValidationException):
            HashedPassword("")

    def test_invalid_hash_format_raises_error(self) -> None:
        """Test invalid hash format raises validation error."""
        with pytest.raises(ValidationException):
            HashedPassword("not-a-valid-hash")

    def test_hashed_password_str_is_masked(self) -> None:
        """Test hashed password string representation is masked."""
        bcrypt_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
        hashed = HashedPassword(bcrypt_hash)
        assert "[HASHED]" in str(hashed)
        assert bcrypt_hash not in str(hashed)

