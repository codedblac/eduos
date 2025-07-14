from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allows only institution admins to perform write operations.
    Everyone else gets read-only access.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'is_institution_admin', False)

    def __str__(self):
        return "IsInstitutionAdminOrReadOnly"


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Teachers can access their own timetable entries.
    Institution admins have unrestricted access.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, 'is_institution_admin', False):
            return True
        if hasattr(user, 'teacher') and hasattr(obj, 'teacher'):
            return obj.teacher == user.teacher
        return False

    def has_permission(self, request, view):
        user = request.user
        return getattr(user, 'is_institution_admin', False) or hasattr(user, 'teacher')

    def __str__(self):
        return "IsTeacherOrAdmin"


class IsTimetableEditor(permissions.BasePermission):
    """
    Allows users with the 'edit_timetable' permission or institution admins
    to perform timetable edit actions.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            getattr(user, 'is_institution_admin', False) or
            (hasattr(user, 'has_permission') and user.has_permission('edit_timetable'))
        )

    def __str__(self):
        return "IsTimetableEditor"
