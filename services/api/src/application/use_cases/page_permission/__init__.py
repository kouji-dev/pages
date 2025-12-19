"""Page permission use cases."""

from src.application.use_cases.page_permission.get_page_permissions import (
    GetPagePermissionsUseCase,
)
from src.application.use_cases.page_permission.get_space_permissions import (
    GetSpacePermissionsUseCase,
)
from src.application.use_cases.page_permission.update_page_permissions import (
    UpdatePagePermissionsUseCase,
)
from src.application.use_cases.page_permission.update_space_permissions import (
    UpdateSpacePermissionsUseCase,
)

__all__ = [
    "GetPagePermissionsUseCase",
    "UpdatePagePermissionsUseCase",
    "GetSpacePermissionsUseCase",
    "UpdateSpacePermissionsUseCase",
]
