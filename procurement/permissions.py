from rest_framework import permissions
from accounts.models import CustomUser

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsInstitutionMember(permissions.BasePermission):
    """
    Restricts access to users acting within their institution.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, 'institution'):
            return obj.institution == user.institution
        if hasattr(obj, 'request') and hasattr(obj.request, 'institution'):
            return obj.request.institution == user.institution
        return False

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'institution')


# ----------------------------
# Role-Based Access
# ----------------------------

class IsProcurementOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role in ['procurement_officer', 'admin', 'super_admin']


class IsDepartmentHead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role in ['department_head', 'admin', 'super_admin']


class IsFinanceManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role in ['finance_manager', 'admin', 'super_admin']


class IsStoreClerk(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role in ['store_clerk', 'admin', 'super_admin']


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role== 'super_admin'


class IsAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.primary_role in ['admin', 'super_admin']


# ----------------------------
# Object-Level Permissions
# ----------------------------

class IsRequestOwnerOrAdmin(permissions.BasePermission):
    """
    Only the original requester, admin, or super admin can modify a procurement request.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.requested_by or
            request.user.primary_role in ['admin', 'super_admin'] or
            request.user.is_superuser
        )


class IsInvoiceUnpaidAndFinanceManager(permissions.BasePermission):
    """
    Only finance manager can pay unpaid invoices.
    """

    def has_object_permission(self, request, view, obj):
        return (
            not obj.is_paid and
            request.user.primary_role in ['finance_manager', 'admin', 'super_admin']
        )


class IsApproverForRequest(permissions.BasePermission):
    """
    Checks if user is in position to approve the request.
    (Handled manually in view logic usually)
    """

    def has_permission(self, request, view):
        return request.user.primary_role in [
            'finance_manager', 'admin', 'super_admin', 'department_head'
        ]
