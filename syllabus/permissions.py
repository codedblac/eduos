from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access only to admin users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Write permissions for institutional admins, read-only for others.
    Assumes `request.user.institution` exists.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'institution')


class IsTeacherOrAdminCanEdit(permissions.BasePermission):
    """
    Teachers can update progress; only admins can edit syllabus content.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # If updating progress
        if hasattr(obj, 'teacher') and obj.teacher == request.user:
            return True

        # Only admin or staff can modify
        return request.user.is_authenticated and request.user.is_staff


class IsSyllabusOwnerOrAdmin(permissions.BasePermission):
    """
    Only the user who created the item or an admin can modify it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.created_by == request.user or request.user.is_staff
