# assessments/permissions.py

from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows full access to admins, read-only for others.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'is_admin', False):
                return True
            return request.method in permissions.SAFE_METHODS
        return False


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Allows access to teachers and admins.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                getattr(request.user, 'is_teacher', False) or
                getattr(request.user, 'is_admin', False) or
                request.user.is_superuser
            )
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to owners of an object or admins.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or getattr(request.user, 'is_admin', False):
            return True
        return obj.user == request.user  # assumes `user` is the owner field


class IsStudentViewingOwn(permissions.BasePermission):
    """
    Students can only view their own assessment records.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and getattr(request.user, 'is_student', False):
            return obj.student.user == request.user
        return False


class IsTeacherOfClassOrAdmin(permissions.BasePermission):
    """
    Used in assessments to restrict teachers to only their class/subject assessments.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or getattr(user, 'is_admin', False):
            return True

        # If the object has a `created_by` or `teacher` field
        if hasattr(obj, 'teacher'):
            return obj.teacher == user
        if hasattr(obj, 'created_by'):
            return obj.created_by == user
        return False
