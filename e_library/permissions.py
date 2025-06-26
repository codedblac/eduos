from rest_framework import permissions


class IsInstitutionUploaderOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for all, but editing/deleting only for the original uploader or super admins.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Public read access depending on visibility
            if obj.visibility == 'public':
                return True
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                return obj.institution == request.user.profile.institution
            return False

        # Write access
        if not request.user.is_authenticated:
            return False

        # Uploader or super admin (e.g., school head)
        return obj.uploader == request.user.profile or request.user.profile.role in ['admin', 'super_admin']


class IsSchoolTeacherOrAdmin(permissions.BasePermission):
    """
    Allows only authenticated institution teachers or admins to upload resources.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False
        return user.profile.role in ['teacher', 'admin', 'super_admin']


class IsAIOrAdmin(permissions.BasePermission):
    """
    Used internally by the AI engine to allow updates (e.g., auto tagging or summaries).
    Only admins and trusted AI systems can use this.
    """

    def has_permission(self, request, view):
        # AI access (e.g., internal system or staff token)
        return request.user and (request.user.is_staff or getattr(request, "from_ai", False))


class IsStudentOfInstitution(permissions.BasePermission):
    """
    Restricts student access to resources only from their institution.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False
        return user.profile.institution == obj.institution and user.profile.role == 'student'
