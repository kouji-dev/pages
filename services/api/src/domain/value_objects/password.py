"""Password value objects."""

import re
from dataclasses import dataclass

from src.domain.exceptions import ValidationException


@dataclass(frozen=True, slots=True)
class Password:
    """Plain password value object with strength validation.
    
    Immutable value object that validates password strength on creation.
    This should only be used temporarily and never stored.
    """

    value: str

    # Minimum 8 characters
    MIN_LENGTH = 8
    # Maximum 128 characters
    MAX_LENGTH = 128

    def __post_init__(self) -> None:
        """Validate password strength on creation."""
        if not self.value:
            raise ValidationException("Password cannot be empty", field="password")
        
        if len(self.value) < self.MIN_LENGTH:
            raise ValidationException(
                f"Password must be at least {self.MIN_LENGTH} characters long",
                field="password",
            )
        
        if len(self.value) > self.MAX_LENGTH:
            raise ValidationException(
                f"Password cannot exceed {self.MAX_LENGTH} characters",
                field="password",
            )
        
        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", self.value):
            raise ValidationException(
                "Password must contain at least one uppercase letter",
                field="password",
            )
        
        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", self.value):
            raise ValidationException(
                "Password must contain at least one lowercase letter",
                field="password",
            )
        
        # Check for at least one digit
        if not re.search(r"\d", self.value):
            raise ValidationException(
                "Password must contain at least one digit",
                field="password",
            )
        
        # Check for at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'`~]", self.value):
            raise ValidationException(
                "Password must contain at least one special character",
                field="password",
            )

    def __str__(self) -> str:
        """Return masked password for security."""
        return "********"

    def __repr__(self) -> str:
        """Return masked representation."""
        return "Password(********)"

    @property
    def strength(self) -> str:
        """Calculate password strength based on objective criteria.
        
        Strength is determined by:
        - Length (more is better, minimum = weak baseline)
        - Character variety (mixed case, digits, special chars)
        - Complexity (unique characters, patterns)
        
        Returns:
            'weak', 'medium', or 'strong'
        """
        score = 0
        length = len(self.value)
        
        # Length scoring (longer is significantly better)
        if length >= 16:
            score += 4
        elif length >= 12:
            score += 2
        elif length >= 11:
            score += 2  # 11-12 chars get same bonus to reward longer passwords
        elif length >= 10:
            score += 1
        # 8-9 characters: 0 points (just meets minimum, baseline for weak)
        
        # Character variety (each type adds to strength)
        has_upper = bool(re.search(r"[A-Z]", self.value))
        has_lower = bool(re.search(r"[a-z]", self.value))
        has_digit = bool(re.search(r"\d", self.value))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'`~]", self.value))
        
        # Variety score (all 4 types required, but having them all = 2 points)
        variety_count = sum([has_upper, has_lower, has_digit, has_special])
        if variety_count == 4:
            score += 2
        elif variety_count == 3:
            score += 1
        # 1-2 types: 0 points (shouldn't happen due to validation, but safety)
        
        # Complexity scoring (unique characters add strength)
        unique_chars = len(set(self.value))
        if unique_chars >= 12:
            score += 2
        elif unique_chars >= 8:
            score += 1
        # < 8 unique: 0 points
        
        # Pattern penalty: sequences reduce strength (common weak pattern)
        # Only apply penalty if password is short (< 10 chars) OR has limited variety
        # Passwords >= 10 chars with full variety can tolerate sequences
        has_sequence = bool(
            re.search(r"(012|123|234|345|456|567|678|789|890)", self.value) or
            re.search(r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)", self.value, re.IGNORECASE)
        )
        # Only penalize sequences if password is short OR doesn't have full variety
        if has_sequence and (length < 10 or variety_count < 4):
            score -= 1
        
        # Determine strength based on total score
        # Thresholds: weak (0-4), medium (5-7), strong (8+)
        # Adjusted to account for password length being the primary factor
        if score >= 8:
            return "strong"
        elif score >= 5:
            return "medium"
        return "weak"


@dataclass(frozen=True, slots=True)
class HashedPassword:
    """Hashed password value object.
    
    Immutable value object representing a hashed password.
    This is safe to store in the database.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate hashed password."""
        if not self.value:
            raise ValidationException("Hashed password cannot be empty")
        
        # Basic validation - bcrypt hashes start with $2b$ or $2a$
        if not self.value.startswith(("$2b$", "$2a$", "$argon2")):
            raise ValidationException("Invalid password hash format")

    def __str__(self) -> str:
        """Return masked hash for security."""
        return "[HASHED]"

    def __repr__(self) -> str:
        """Return masked representation."""
        return "HashedPassword([HASHED])"

