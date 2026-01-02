from django.urls import path
from .views import (
    SystemModuleListView,
    PlanListCreateView,
    AssignModuleToSchoolView,
    AssignModulesToUserView,
    CurrentUserModulesView,
)

app_name = "modules"

urlpatterns = [
    # List all system modules (Super Admin only)
    path("system-modules/", SystemModuleListView.as_view(), name="system-modules-list"),

    # List and create plans (Super Admin only)
    path("plans/", PlanListCreateView.as_view(), name="plans-list-create"),

    # Assign modules to a school (Super Admin / Onboarding)
    path("assign-school/", AssignModuleToSchoolView.as_view(), name="assign-module-school"),

    # Assign modules to a user (Institution Admin)
    path("assign-user/", AssignModulesToUserView.as_view(), name="assign-module-user"),

    # Get modules for the current logged-in user (dynamic sidebar)
    path("my-modules/", CurrentUserModulesView.as_view(), name="current-user-modules"),
]
