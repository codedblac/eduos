from rest_framework import permissions


class IsAcademicAdminOrReadOnly(permissions.BasePermission):
    """
    Allows full access to users with 'academic_admin' role or institution admin,
    read-only access to others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return user.is_authenticated and (
            user.is_superuser or
            getattr(user, 'is_institution_admin', False) or
            getattr(user, 'role', '') in ['academic_admin']
        )


class IsAcademicEditor(permissions.BasePermission):
    """
    Only users with specific academic roles can modify entries.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role in ['academic_admin', 'institution_admin']
        )
