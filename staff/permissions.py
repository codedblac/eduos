# staff/permissions.py

from rest_framework import permissions

class IsHRStaff(permissions.BasePermission):
    """
    Allows access only to HR-designated users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role== 'hr'

class IsSelfOrHR(permissions.BasePermission):
    """
    Allows staff to view/update their own records or HR to access any.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user == obj.user or request.user.primary_role== 'hr'
        )

class IsHROrReadOnly(permissions.BasePermission):
    """
    HR has full access; others can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.primary_role== 'hr'

class IsHROrInstitutionAdmin(permissions.BasePermission):
    """
    Allows only HR or institution-level admins to perform actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.primary_role in ['hr', 'admin', 'institution_admin']
        )
