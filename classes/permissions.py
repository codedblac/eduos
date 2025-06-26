# classes/permissions.py
from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to users with super admin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'

class CanManageClasses(permissions.BasePermission):
    """
    Allows access to users who can manage classes in their institution:
    e.g. superadmins and school admins.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['superadmin', 'admin', 'schooladmin']
