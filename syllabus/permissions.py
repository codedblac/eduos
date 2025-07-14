from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone.
    Write access only to system admins (is_staff).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Institutional admins can write, everyone else read-only.
    Assumes `request.user.institution` exists and institution admin flag is implemented.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return (
            user.is_authenticated and
            hasattr(user, 'institution') and
            (user.is_staff or getattr(user, 'is_institution_admin', False))
        )


class IsTeacherOrAdminCanEdit(permissions.BasePermission):
    """
    Teachers can update their own syllabus progress.
    Only institutional admins/staff can modify syllabus content.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user

        # Progress update by the teacher
        if hasattr(obj, 'teacher') and obj.teacher == user:
            return True

        # Syllabus-level write access
        return user.is_authenticated and (user.is_staff or getattr(user, 'is_institution_admin', False))


class IsSyllabusOwnerOrAdmin(permissions.BasePermission):
    """
    Write permissions allowed only to the user who created the object or admins.
    Read access allowed to all authenticated users.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return user.is_authenticated and (obj.created_by == user or user.is_staff or getattr(user, 'is_institution_admin', False))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Generic permission class for models with `created_by`.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.created_by == request.user or request.user.is_staff


class IsAuthenticatedAndFromSameInstitution(permissions.BasePermission):
    """
    Ensure object belongs to same institution as the user.
    Can be used with list views or filter sets.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'institution')

    def has_object_permission(self, request, view, obj):
        return (
            request.user and request.user.is_authenticated and
            hasattr(request.user, 'institution') and
            getattr(obj, 'institution', None) == request.user.institution
        )
