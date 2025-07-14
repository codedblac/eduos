from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only institution admins can modify, others can read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'is_institution_admin', False)


class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only super admins can write. Everyone else has read access.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'is_superadmin', False)


class IsEventOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the event creator or superadmin can update/delete academic events.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.institution == getattr(request.user, 'institution', None) and
            (getattr(request.user, 'is_institution_admin', False) or getattr(request.user, 'is_superadmin', False))
        )


class IsAuditViewer(permissions.BasePermission):
    """
    View-only permission for audit logs.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS and request.user.is_authenticated
