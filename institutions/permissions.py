from rest_framework import permissions
from accounts.models import CustomUser


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to Super Admins."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role== CustomUser.Role.SUPER_ADMIN


class IsInstitutionAdmin(permissions.BasePermission):
    """Allows access only to Institution Admins."""

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.primary_role== CustomUser.Role.ADMIN and user.institution is not None


class IsSameInstitutionOrSuperAdmin(permissions.BasePermission):
    """
    Grants access if user is Super Admin or object belongs to the same institution.
    Used for models with an `institution` FK.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.primary_role== CustomUser.Role.SUPER_ADMIN:
            return True
        return getattr(obj, 'institution', None) == user.institution


class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """
    Super Admins can read/write. Others only have read access.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.primary_role== CustomUser.Role.SUPER_ADMIN


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Institution Admins can create/update/delete within their institution.
    Super Admins have full access. Others can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated and
            user.primary_role in [CustomUser.Role.ADMIN, CustomUser.Role.SUPER_ADMIN]
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if user.primary_role== CustomUser.Role.SUPER_ADMIN:
            return True
        return getattr(obj, 'institution', None) == user.institution


class CanManageInstitutionData(permissions.BasePermission):
    """
    Super Admins can manage any institution.
    Institution Admins can read and manage their own institution's related data.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.primary_role== CustomUser.Role.SUPER_ADMIN:
            return True
        return request.method in permissions.SAFE_METHODS and user.primary_role== CustomUser.Role.ADMIN

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.primary_role== CustomUser.Role.SUPER_ADMIN:
            return True
        return getattr(obj, 'institution', None) == user.institution


class IsInstitutionMember(permissions.BasePermission):
    """
    Allows access only to users associated with an institution.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and getattr(user, 'institution', None) is not None
