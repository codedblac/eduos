from rest_framework import permissions


class IsExamCreatorOrAdmin(permissions.BasePermission):
    """
    Allows access only to exam creators or superusers.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or getattr(obj, 'created_by', None) == request.user


class IsInstitutionStaffOrReadOnly(permissions.BasePermission):
    """
    Allow full access to staff from the same institution; others are read-only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and
            getattr(request.user, 'institution', None) == getattr(obj, 'institution', None)
        )


class IsResultOwnerOrAdmin(permissions.BasePermission):
    """
    Students can view their own results. Admins can view/edit all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if hasattr(obj, 'student') and hasattr(obj.student, 'user'):
            return obj.student.user == request.user and request.method in permissions.SAFE_METHODS
        return False


class IsPredictionCreatorOrAdmin(permissions.BasePermission):
    """
    Only the prediction creator or an admin can access or modify it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or getattr(obj, 'created_by', None) == request.user


class IsExamResultManager(permissions.BasePermission):
    """
    Permissions for users explicitly assigned to 'ExamResultManagers' group.
    Extendable with institution roles in future.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='ExamResultManagers').exists()
        )


class IsGradeManagerOrReadOnly(permissions.BasePermission):
    """
    Allow only superusers to manage grade boundaries; others have read-only access.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.is_superuser
        )
