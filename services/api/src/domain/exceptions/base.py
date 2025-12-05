"""Base domain exceptions."""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain exceptions."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str | int) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class ValidationException(DomainException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        details = {"field": field} if field else {}
        super().__init__(message=message, details=details)


class AuthenticationException(DomainException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message)


class AuthorizationException(DomainException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message)


class ConflictException(DomainException):
    """Raised when there's a conflict (e.g., duplicate email)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        details = {"field": field} if field else {}
        super().__init__(message=message, details=details)


class StorageException(DomainException):
    """Raised when storage operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message)
