from rest_framework import permissions
from .models import DepartmentUser


class IsHOD(permissions.BasePermission):
    """
    Allows access only to users who are Heads of Department (HOD).
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            role=DepartmentUser.HOD,
            is_active=True
        ).exists()


class IsDeputyHOD(permissions.BasePermission):
    """
    Allows access only to Deputy Heads of Department.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            role=DepartmentUser.DEPUTY_HOD,
            is_active=True
        ).exists()


class IsDepartmentMember(permissions.BasePermission):
    """
    Allows access to any active member of a department (including HOD, Deputy, Member).
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            is_active=True
        ).exists()


class IsHODOrDeputyHOD(permissions.BasePermission):
    """
    Allows access if user is HOD or Deputy HOD.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            role__in=[DepartmentUser.HOD, DepartmentUser.DEPUTY_HOD],
            is_active=True
        ).exists()


class IsHODAndOwnDepartment(permissions.BasePermission):
    """
    Ensures HOD is managing only their own department.
    """

    def has_object_permission(self, request, view, obj):
        return DepartmentUser.objects.filter(
            user=request.user,
            department=obj,
            role=DepartmentUser.HOD,
            is_active=True
        ).exists()


class CanManageDepartmentUsers(permissions.BasePermission):
    """
    HOD can assign/remove department roles.
    """

    def has_permission(self, request, view):
        return DepartmentUser.objects.filter(
            user=request.user,
            role=DepartmentUser.HOD,
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        return obj.department.members.filter(
            user=request.user,
            role=DepartmentUser.HOD,
            is_active=True
        ).exists()
