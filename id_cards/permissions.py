from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access to institution admins. Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, 'institutionadmin', None) is not None


class CanManageOwnInstitutionIDCards(permissions.BasePermission):
    """
    Allow managing ID cards only if user is from the same institution.
    """
    def has_object_permission(self, request, view, obj):
        user_institution = getattr(request.user, 'institution', None)
        object_institution = getattr(obj, 'institution', None)

        return user_institution is not None and user_institution == object_institution


class IsOwnerOrInstitutionAdmin(permissions.BasePermission):
    """
    Allow access to users for their own ID cards; admins of the institution have full access.
    """
    def has_object_permission(self, request, view, obj):
        is_owner = request.user == getattr(obj, 'user', None)
        is_admin = request.user.is_authenticated and getattr(request.user, 'institutionadmin', None) is not None
        return is_owner or is_admin
