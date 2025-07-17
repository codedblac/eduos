# lessons/permissions.py

from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Full access for institutional admins. Read-only for others.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'institution') and request.user.is_institution_admin


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users who are teachers or admins.
    Assumes user roles are defined in user.role or a user.groups/permissions system.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user and user.is_authenticated and (
                getattr(user, 'is_staff', False) or
                getattr(user, 'is_superuser', False) or
                getattr(user, 'role', '').lower() == 'teacher' or
                'teacher' in [g.name.lower() for g in user.groups.all()]
            )
        )

class IsLessonOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow only the teacher who owns the lesson to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user or request.user.is_superuser


class IsLessonRecorderOrAdmin(permissions.BasePermission):
    """
    Only the person who recorded a lesson or an admin can edit it.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
               obj.recorded_by == request.user or \
               request.user.is_superuser


class IsHODOrTeacherOrReadOnly(permissions.BasePermission):
    """
    Allow HODs or assigned teachers to create/update lesson plans, else read-only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or
             getattr(request.user, 'is_head_of_department', False) or
             getattr(request.user, 'is_teacher', False))
        )
