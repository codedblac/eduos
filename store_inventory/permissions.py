# permissions.py
from rest_framework import permissions

class IsInstitutionMember(permissions.BasePermission):
    """
    Allows access only to users who belong to the same institution as the object
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'institution')

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'institution') and obj.institution == request.user.institution


class IsStoreManagerOrReadOnly(permissions.BasePermission):
    """
    Allow full access to store managers, read-only access to others in the same institution
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return hasattr(request.user, 'institution')
        return request.user.primary_role in ['admin', 'store_manager']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.institution == request.user.institution
        return request.user.primary_role in ['admin', 'store_manager'] and obj.institution == request.user.institution
