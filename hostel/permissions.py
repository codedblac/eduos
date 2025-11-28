from rest_framework import permissions


class IsInstitutionMember(permissions.BasePermission):
    """
    Allows access only to users from the same institution.
    """
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, 'institution') and obj.institution == request.user.institution


class IsHostelManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow hostel managers to edit objects.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.primary_role in ['admin', 'hostel_manager']

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and obj.institution == request.user.institution
