"""Email value object."""

import re
from dataclasses import dataclass

from src.domain.exceptions import ValidationException


@dataclass(frozen=True, slots=True)
class Email:
    """Email value object with validation.
    
    Immutable value object that validates email format on creation.
    """

    value: str

    # RFC 5322 compliant email regex (simplified version)
    _EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __post_init__(self) -> None:
        """Validate email on creation."""
        if not self.value:
            raise ValidationException("Email cannot be empty", field="email")
        
        normalized = self.value.lower().strip()
        
        if not self._EMAIL_REGEX.match(normalized):
            raise ValidationException("Invalid email format", field="email")
        
        if len(normalized) > 255:
            raise ValidationException("Email is too long (max 255 characters)", field="email")
        
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        """Return email as string."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare emails."""
        if isinstance(other, Email):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower()
        return False

    def __hash__(self) -> int:
        """Hash email."""
        return hash(self.value)

    @property
    def domain(self) -> str:
        """Get email domain."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Get local part of email (before @)."""
        return self.value.split("@")[0]

