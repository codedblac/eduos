from rest_framework import permissions


class IsMaintenanceAdmin(permissions.BasePermission):
    """
    Allows access only to maintenance admins or superusers.
    """

    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or request.user.role == 'maintenance_admin'
        )


class IsMaintenanceStaffOrAdmin(permissions.BasePermission):
    """
    Allows access to maintenance staff or admins.
    """

    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or
            request.user.role in ['maintenance_admin', 'maintenance_staff']
        )


class IsReporterOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user and (
            request.user.is_superuser or
            obj.reported_by == request.user or
            request.user.role == 'maintenance_admin'
        )


class IsTechnicianOrReadOnly(permissions.BasePermission):
    """
    Technicians can edit; others read-only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.role in ['maintenance_staff', 'maintenance_admin']
