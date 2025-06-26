# institutions/permissions.py
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to super admins (e.g., school principals or platform superusers).
    Super admins can manage all institutions and their details.
    """

    def has_permission(self, request, view):
        user = request.user
        # Assuming 'super_admin' is the role for principals or platform superusers
        return user.is_authenticated and getattr(user, 'role', None) == 'super_admin'


class CanManageInstitution(permissions.BasePermission):
    """
    Allows access to users who can manage a specific institution.
    For example: admins or users assigned to that institution.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        # Super admins can manage all
        if getattr(user, 'role', None) == 'super_admin':
            return True

        # Otherwise, check if user belongs to this institution and has admin or equivalent rights
        if hasattr(user, 'institution') and user.institution == obj:
            return user.role in ['admin', 'bursar', 'finance_officer', 'hostel_manager']

        return False


class CanManageSchoolAccounts(permissions.BasePermission):
    """
    Allows users who can manage school financial accounts:
    Usually admin, bursar, finance officer roles at the institution.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Super admins can manage all
        if getattr(user, 'role', None) == 'super_admin':
            return True

        # Check if user has rights in their institution
        return user.role in ['admin', 'bursar', 'finance_officer']

    def has_object_permission(self, request, view, obj):
        # Object-level permission for SchoolAccount
        user = request.user
        if getattr(user, 'role', None) == 'super_admin':
            return True

        # User must belong to institution of the account
        return obj.institution == getattr(user, 'institution', None) and user.role in ['admin', 'bursar', 'finance_officer']
