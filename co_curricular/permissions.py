# co_curricular/permissions.py

from rest_framework import permissions


class IsAdminOrActivityManager(permissions.BasePermission):
    """
    Allows access only to admins and users assigned as activity heads or patrons.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['Admin', 'ActivityHead', 'CoCurricularManager']).exists()
        )


class IsStudentOwnerOrReadOnly(permissions.BasePermission):
    """
    Students can only view their own portfolios and participation.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.student.user == request.user or request.user.is_superuser
        return False


class IsCoachOrReadOnly(permissions.BasePermission):
    """
    Allows coaches or patrons to update participation logs but others only read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.activity_head or request.user.is_superuser


class IsStudentUser(permissions.BasePermission):
    """
    Grants access only to authenticated users who are students.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Student').exists()


class IsParentUser(permissions.BasePermission):
    """
    Grants view-only access to guardians or parents.
    """
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name__in=['Parent', 'Guardian']).exists() and
            request.method in permissions.SAFE_METHODS
        )
