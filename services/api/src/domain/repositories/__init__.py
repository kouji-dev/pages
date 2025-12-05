"""Domain repository interfaces (ports)."""

from src.domain.repositories.organization_repository import OrganizationRepository
from src.domain.repositories.user_repository import UserRepository

__all__ = ["UserRepository", "OrganizationRepository"]
