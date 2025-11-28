from rest_framework import permissions
from accounts.models import CustomUser


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to super admins."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role == CustomUser.Role.SUPER_ADMIN
        )


class IsInstitutionAdmin(permissions.BasePermission):
    """Allow access only to institution admins."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role == CustomUser.Role.INSTITUTION_ADMIN
        )


class IsInstitutionStaff(permissions.BasePermission):
    """Allow institution-linked users except public/government users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.institution is not None and
            request.user.primary_role not in [
                CustomUser.Role.SUPER_ADMIN,
                CustomUser.Role.PUBLIC_LEARNER,
                CustomUser.Role.PUBLIC_TEACHER,
                CustomUser.Role.GOV_USER
            ]
        )


class IsPublicUser(permissions.BasePermission):
    """Allow access only to public users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role in [
                CustomUser.Role.PUBLIC_LEARNER,
                CustomUser.Role.PUBLIC_TEACHER
            ]
        )


class IsGovernmentUser(permissions.BasePermission):
    """Allow access only to government users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role == CustomUser.Role.GOV_USER
        )


class IsSameInstitutionOrSuperAdmin(permissions.BasePermission):
    """
    Allow if user belongs to the same institution
    OR user is SUPER_ADMIN
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.primary_role == CustomUser.Role.SUPER_ADMIN:
            return True
        return getattr(obj, 'institution', None) == user.institution


class IsSameInstitution(permissions.BasePermission):
    """
    Only users from the same institution.
    SUPER_ADMIN is NOT allowed bypass.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated and
            getattr(obj, 'institution', None) == user.institution
        )
