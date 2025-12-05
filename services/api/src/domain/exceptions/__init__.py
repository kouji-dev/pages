"""Domain exceptions."""

from src.domain.exceptions.base import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DomainException,
    EntityNotFoundException,
    ValidationException,
)

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ConflictException",
]
