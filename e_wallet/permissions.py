# e_wallet/permissions.py

from rest_framework import permissions
from accounts.models import CustomUser


class IsAdminOrFinance(permissions.BasePermission):
    """
    Grants full access to superusers, institutional admins, finance officers, bursars, or principals.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or
            user.primary_role in ['admin', 'finance', 'bursar', 'principal']
        )


class IsParent(permissions.BasePermission):
    """
    Grants access to parents or guardians.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role== 'parent'


class IsStudent(permissions.BasePermission):
    """
    Grants access to students only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role== 'student'


class IsTeacher(permissions.BasePermission):
    """
    Grants access to teachers.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role== 'teacher'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Students and parents can access their own or their child’s data.
    Admins and finance users have full access.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin override
        if user.is_superuser or user.primary_role in ['admin', 'finance']:
            return True

        # Student access to own wallet
        if hasattr(obj, 'student') and user.primary_role== 'student':
            return obj.student.user == user

        # Parent access to child's wallet
        if hasattr(obj, 'student') and user.primary_role== 'parent':
            return obj.student.guardians.filter(id=user.id).exists()

        # Safe methods allowed for everyone with permission
        return request.method in permissions.SAFE_METHODS


class CanInitiateMicroFees(permissions.BasePermission):
    """
    Allows teachers or admin roles to initiate micro-fees (e.g., remedial, trips).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['teacher', 'admin']


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Allows object owners or admin staff to view or edit; read-only for others.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.primary_role in ['admin', 'finance']:
            return True

        if hasattr(obj, 'parent') and obj.parent == user:
            return True

        if hasattr(obj, 'student') and user.primary_role== 'student':
            return obj.student.user == user

        return request.method in permissions.SAFE_METHODS
