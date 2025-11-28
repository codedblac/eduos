from rest_framework import permissions

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

# Define role groups once for clarity and reuse
FINANCE_ADMIN_ROLES = ['admin', 'finance_head']
ACCOUNTANT_ROLES = ['accountant', 'finance_clerk']
AUDITOR_ROLES = ['auditor']
INSTITUTION_STAFF_ROLES = ['admin', 'finance_head', 'accountant', 'auditor', 'principal', 'deputy']
FINANCE_ROLES = FINANCE_ADMIN_ROLES + ACCOUNTANT_ROLES + AUDITOR_ROLES


class IsFinanceAdmin(permissions.BasePermission):
    """
    Full access to all finance operations.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in FINANCE_ADMIN_ROLES


class IsAccountant(permissions.BasePermission):
    """
    Can perform transactional finance operations (income, expenses, waivers).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ACCOUNTANT_ROLES


class IsAuditorOrReadOnly(permissions.BasePermission):
    """
    Can view all finance data but not modify.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.primary_role in AUDITOR_ROLES or request.method in SAFE_METHODS
        )


class IsRefundApprover(permissions.BasePermission):
    """
    Can approve waivers, refunds, or other financial requests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in FINANCE_ADMIN_ROLES


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows students or guardians to view their own finance-related objects.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if hasattr(obj, 'student'):
                student = obj.student
                user = request.user
                return (
                    hasattr(student, 'user') and student.user == user
                ) or (
                    hasattr(student, 'guardians') and student.guardians.filter(user=user).exists()
                )
        return False


class IsInstitutionStaff(permissions.BasePermission):
    """
    Read access for institutional leadership and finance staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in INSTITUTION_STAFF_ROLES


class IsFinanceRole(permissions.BasePermission):
    """
    General permission for finance-related operations.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in FINANCE_ROLES


class IsFinanceClerkOrReadOnly(permissions.BasePermission):
    """
    Clerks can write; all others read-only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.primary_role== 'finance_clerk' or request.method in SAFE_METHODS
        )


class IsBudgetEditor(permissions.BasePermission):
    """
    Only finance_head or admin can create or edit budgets.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['finance_head', 'admin']


class IsJournalPoster(permissions.BasePermission):
    """
    Only users with specific rights can post journal entries.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['admin', 'accountant']
