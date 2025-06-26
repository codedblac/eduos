# finance/permissions.py

from rest_framework import permissions

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsFinanceAdmin(permissions.BasePermission):
    """
    Full access to all finance operations.
    Intended for senior finance roles (e.g. Finance Director, School Admin).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'finance_head']


class IsAccountant(permissions.BasePermission):
    """
    Can perform transactional finance operations (income, expense, refund).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['accountant', 'finance_clerk']


class IsAuditorOrReadOnly(permissions.BasePermission):
    """
    Can view all finance data but not alter it.
    Intended for external/internal audit roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'auditor' or request.method in SAFE_METHODS
        )


class IsRefundApprover(permissions.BasePermission):
    """
    Permission for those allowed to approve financial requests (e.g. waivers, refunds).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['finance_head', 'admin']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission for students or guardians viewing their own finance info.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if hasattr(obj, 'student'):
                student = obj.student
                return student.user == request.user or student.guardians.filter(user=request.user).exists()
        return False


class IsInstitutionStaff(permissions.BasePermission):
    """
    General permission for institutional staff with read access.
    (e.g., principal, deputy, or system-linked support staff)
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'admin', 'finance_head', 'accountant', 'auditor', 'principal', 'deputy'
        ]


class IsFinanceRole(permissions.BasePermission):
    """
    Generic finance access control for any finance-linked role.
    Can be used when writing DRY custom views for shared access logic.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'admin', 'finance_head', 'accountant', 'finance_clerk', 'auditor'
        ]
