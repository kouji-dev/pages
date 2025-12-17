"""Dashboard use cases."""

from src.application.use_cases.dashboard.create_dashboard import CreateDashboardUseCase
from src.application.use_cases.dashboard.delete_dashboard import DeleteDashboardUseCase
from src.application.use_cases.dashboard.get_dashboard import GetDashboardUseCase
from src.application.use_cases.dashboard.get_widget_data import GetWidgetDataUseCase
from src.application.use_cases.dashboard.list_dashboards import ListDashboardsUseCase
from src.application.use_cases.dashboard.update_dashboard import UpdateDashboardUseCase

__all__ = [
    "CreateDashboardUseCase",
    "GetDashboardUseCase",
    "ListDashboardsUseCase",
    "UpdateDashboardUseCase",
    "DeleteDashboardUseCase",
    "GetWidgetDataUseCase",
]
