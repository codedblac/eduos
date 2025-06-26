from rest_framework import permissions


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only teachers to edit their lessons.
    Admins and HoDs can view/edit all.
    """

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True

        return getattr(obj, 'teacher', None) == request.user or \
               getattr(obj, 'recorded_by', None) == request.user or \
               getattr(getattr(obj, 'lesson_plan', None), 'teacher', None) == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    General purpose owner/admin permission
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.uploaded_by == request.user
