from rest_framework import permissions
from accounts.models import CustomUser


class IsSuperAdmin(permissions.BasePermission):
    """
    ✅ Allows access only to super admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == CustomUser.Role.SUPER_ADMIN


class IsInstitutionAdmin(permissions.BasePermission):
    """
    ✅ Allows access only to institution (school) admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == CustomUser.Role.ADMIN


class IsInstitutionStaff(permissions.BasePermission):
    """
    ✅ Allows access only to institutional users (staff, teacher, etc.).
    Excludes public and government roles.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.institution is not None and
            request.user.role not in [
                CustomUser.Role.SUPER_ADMIN,
                CustomUser.Role.PUBLIC_LEARNER,
                CustomUser.Role.PUBLIC_TEACHER,
                CustomUser.Role.GOV_USER
            ]
        )


class IsPublicUser(permissions.BasePermission):
    """
    ✅ Allows access only to public platform users (not school-linked).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [
                CustomUser.Role.PUBLIC_LEARNER,
                CustomUser.Role.PUBLIC_TEACHER
            ]
        )


class IsGovernmentUser(permissions.BasePermission):
    """
    ✅ Allows access only to government users for national dashboards.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == CustomUser.Role.GOV_USER
        )


class IsSameInstitutionOrSuperAdmin(permissions.BasePermission):
    """
    ✅ Object-level access: allowed if user is from same institution or is SUPER_ADMIN.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return True
        return hasattr(obj, 'institution') and obj.institution == user.institution


class IsSameInstitution(permissions.BasePermission):
    """
    ✅ Object-level access: only if user is from the same institution.
    SUPER_ADMIN is NOT allowed.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated and
            hasattr(obj, 'institution') and
            obj.institution == user.institution
        )
