from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only the author can edit/delete; others can read.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only methods are allowed for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the author of the announcement
        return obj.author == request.user


class IsInstitutionStaffOrReadOnly(permissions.BasePermission):
    """
    Only institution staff (admin, teacher, etc.) can write; everyone else can read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # You can customize this check as per your roles/flags
        return request.user.is_authenticated and request.user.is_staff


class IsTargetUser(permissions.BasePermission):
    """
    Allows access only to users targeted in the announcement.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # If public announcement, allow
        if obj.is_public:
            return True

        # If the user is the author
        if obj.author == request.user:
            return True

        # Check if user is explicitly targeted
        return obj.targets.filter(user=request.user).exists()


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    """
    Only admins can write; others read-only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)
