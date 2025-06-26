# payroll/permissions.py

from rest_framework import permissions


class IsHR(permissions.BasePermission):
    """
    Allows access only to users in the HR group or with 'is_hr' attribute.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='HR').exists() or getattr(request.user, 'is_hr', False)
        )


class IsFinance(permissions.BasePermission):
    """
    Allows access to users in the Finance group or with 'is_finance' attribute.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='Finance').exists() or getattr(request.user, 'is_finance', False)
        )


class IsHOD(permissions.BasePermission):
    """
    Allows access only to Heads of Department.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_hod', False)


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Staff can view their own payroll data. HR/Finance can access all.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if getattr(request.user, 'is_hr', False) or getattr(request.user, 'is_finance', False):
            return True
        return hasattr(obj, 'staff_profile') and obj.staff_profile.user == request.user


class CanApproveAdvance(permissions.BasePermission):
    """
    Only Finance or HR can approve or reject salary advances.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            getattr(request.user, 'is_hr', False) or getattr(request.user, 'is_finance', False)
        )


class CanProcessPayroll(permissions.BasePermission):
    """
    Finance can process payroll and generate payslips.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            getattr(request.user, 'is_finance', False)
        )
