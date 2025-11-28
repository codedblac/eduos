from rest_framework import permissions


class IsMedicalStaff(permissions.BasePermission):
    """
    Allows access only to users with role 'nurse' or 'doctor'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['nurse', 'doctor']


class IsAdminOrMedicalStaff(permissions.BasePermission):
    """
    Allows access to users with role 'admin', 'super_admin', 'nurse', or 'doctor'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['admin', 'super_admin', 'nurse', 'doctor']


class CanManageInventory(permissions.BasePermission):
    """
    Only nurses, doctors, or admins can manage medicine inventory.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['nurse', 'doctor', 'admin']


class CanViewHealthAnalytics(permissions.BasePermission):
    """
    Admins and medical staff can access AI-generated health insights.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['admin', 'super_admin', 'nurse', 'doctor']
