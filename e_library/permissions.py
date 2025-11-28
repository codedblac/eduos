from rest_framework import permissions


class IsInstitutionUploaderOrReadOnly(permissions.BasePermission):
    """
    SAFE methods allowed for:
        - Public resources
        - Users from same institution (if visibility allows)
    WRITE/DELETE only allowed for:
        - Original uploader
        - Institution admins or super admins
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            if obj.visibility == 'public':
                return True
            if user.is_authenticated and hasattr(user, 'profile'):
                return obj.institution == user.profile.institution
            return False

        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False

        return (
            obj.uploader == user
            or user.profile.primary_role in ['admin', 'super_admin']
            or (hasattr(user, 'institution') and user.institution == obj.institution)
        )


class IsSchoolTeacherOrAdmin(permissions.BasePermission):
    """
    Grants access to users who are 'teacher', 'admin', or 'super_admin'.
    Useful for upload endpoints.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, 'profile')
            and user.profile.primary_role in ['teacher', 'admin', 'super_admin']
        )


class IsAIOrAdmin(permissions.BasePermission):
    """
    Used internally by the AI engine to allow background edits
    (e.g., auto summaries, tags). Admins can also perform this.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user and (
                user.is_staff
                or getattr(request, "from_ai", False)
                or getattr(user, 'is_ai', False)
            )
        )


class IsStudentOfInstitution(permissions.BasePermission):
    """
    Allows students to access resources within their institution.
    Can be used for restricted visibility logic.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, 'profile')
            and user.profile.primary_role== 'student'
            and obj.institution == user.profile.institution
        )


class IsInstitutionAdminOrUploader(permissions.BasePermission):
    """
    Allows only institution-level admin or the original uploader to edit/delete.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False
        return (
            obj.uploader == user
            or user.profile.primary_role in ['admin', 'super_admin']
            or (hasattr(user, 'institution') and user.institution == obj.institution)
        )


class IsModeratorOrUploader(permissions.BasePermission):
    """
    For moderation workflows: uploader can update their resource,
    and admins can approve/reject content.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False
        return (
            obj.uploader == user
            or user.profile.primary_role in ['admin', 'super_admin', 'moderator']
        )
