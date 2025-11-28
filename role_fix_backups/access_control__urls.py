from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet, basename='primary_role')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'user-role-assignments', views.UserRoleAssignmentViewSet, basename='user-role-assignment')
router.register(r'role-permissions', views.RolePermissionViewSet, basename='role-permission')
router.register(r'role-audit-logs', views.RoleAuditLogViewSet, basename='role-audit-log')
router.register(r'permission-audit-logs', views.PermissionAuditLogViewSet, basename='permission-audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
