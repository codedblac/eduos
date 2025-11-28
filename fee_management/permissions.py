# fee_management/permissions.py

from rest_framework import permissions


class IsAdminOrAccountant(permissions.BasePermission):
    """
    Allows access only to admins or accountants.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.primary_role in ['admin', 'accountant'] or request.user.is_superuser)
        )


class IsParentOrGuardian(permissions.BasePermission):
    """
    Allows access only to authenticated parents or guardians.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role in ['parent', 'guardian']
        )


class IsStudent(permissions.BasePermission):
    """
    Allows access only to the student role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role== 'student'
        )


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Read-only for anyone, write only for owner, admin, or accountant.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        is_admin = request.user.primary_role== 'admin' or request.user.is_superuser
        is_accountant = request.user.primary_role== 'accountant'
        is_owner = hasattr(obj, 'student') and obj.student.user == request.user

        return request.user.is_authenticated and (is_owner or is_admin or is_accountant)
