# library/permissions.py

from rest_framework import permissions
from accounts.models import RoleChoices


class IsLibrarian(permissions.BasePermission):
    """
    Allow access only to librarians.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == RoleChoices.LIBRARIAN


class IsStudent(permissions.BasePermission):
    """
    Allow access only to students.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == RoleChoices.STUDENT


class IsTeacher(permissions.BasePermission):
    """
    Allow access only to teachers.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == RoleChoices.TEACHER


class IsAdminOrLibrarian(permissions.BasePermission):
    """
    Allow access to librarians or institution admins.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role in [RoleChoices.ADMIN, RoleChoices.LIBRARIAN]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model has a `user` field.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # So we'll always allow GET, HEAD or OPTIONS.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsInstitutionMember(permissions.BasePermission):
    """
    Ensure the user belongs to the same institution as the object.
    Requires the object to have an `institution` field.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'institution') and hasattr(request.user, 'institution'):
            return obj.institution == request.user.institution
        return False


class IsSuperAdmin(permissions.BasePermission):
    """
    Grant access to platform super admins.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_superuser') and request.user.is_superuser
