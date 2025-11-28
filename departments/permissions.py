# departments/permissions.py

from rest_framework import permissions
from .models import DepartmentUser


class IsHOD(permissions.BasePermission):
    """
    Allows access only to Heads of Departments.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user, primary_role='HOD', is_active=True
        ).exists()


class IsDeputyHOD(permissions.BasePermission):
    """
    Allows access only to Deputy Heads of Departments.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user, primary_role='DEPUTY_HOD', is_active=True
        ).exists()


class IsDepartmentMember(permissions.BasePermission):
    """
    Allows access to any active member of the department.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user, is_active=True
        ).exists()


class IsHODAndOwnDepartment(permissions.BasePermission):
    """
    Grants access only if the user is the HOD of the specific department being accessed.
    Assumes department instance is passed as `self.get_object()` in the view.
    """

    def has_object_permission(self, request, view, obj):
        return DepartmentUser.objects.filter(
            user=request.user,
            department=obj,
            primary_role='HOD',
            is_active=True
        ).exists()


class CanManageDepartmentUsers(permissions.BasePermission):
    """
    Allows only HOD or Deputy HODs to manage department members.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            role__in=['HOD', 'DEPUTY_HOD'],
            is_active=True
        ).exists()

class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access only to users who are institution admins for unsafe methods.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_institution_admin


class IsDepartmentHeadOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow department heads (HOD or Deputy HOD) to edit.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated:
            return False

        # Assumes obj has department or is a department
        department = getattr(obj, 'department', obj)
        return department.members.filter(user=user, role__in=['hod', 'deputy_hod']).exists()


class IsDepartmentMemberOrAdmin(permissions.BasePermission):
    """
    Allow members of the department or institution admins to access.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        department = getattr(obj, 'department', obj)

        return (
            user.is_institution_admin or
            department.members.filter(user=user, is_active=True).exists()
        )


class IsAssignedOrReadOnly(permissions.BasePermission):
    """
    Allow users assigned to a department task to edit, others read-only.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user == getattr(obj, 'assigned_to', None)


class IsUploaderOrReadOnly(permissions.BasePermission):
    """
    Only allow users who uploaded the department document to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.uploaded_by
