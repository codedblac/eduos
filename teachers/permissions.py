from rest_framework import permissions

class IsSuperAdminOrInstitutionAdmin(permissions.BasePermission):
    """
    Permission to allow only superadmins or institution admins to manage teachers.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.role == 'admin'
        )

    def has_object_permission(self, request, view, obj):
        # Superadmin can do anything
        if request.user.is_superuser:
            return True
        # Admins can manage teachers in their own institution
        return obj.institution == request.user.institution
