from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allow only institution admins to edit, others can read only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'institutionadmin')


class CanManageOwnInstitutionIDCards(permissions.BasePermission):
    """
    Ensure only users tied to the same institution can manage their ID cards.
    """
    def has_object_permission(self, request, view, obj):
        user_institution = getattr(request.user, 'institution', None)
        target_institution = getattr(obj, 'institution', None)

        if not user_institution or not target_institution:
            return False

        return user_institution == target_institution


class IsOwnerOrInstitutionAdmin(permissions.BasePermission):
    """
    Allow users to view or manage their own ID cards; institution admins can manage all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user == getattr(obj, 'user', None):
            return True
        return request.user.is_authenticated and hasattr(request.user, 'institutionadmin')
