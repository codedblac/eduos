from rest_framework import permissions
from .models import SharedAccess


class IsUploaderOrAdmin(permissions.BasePermission):
    """
    Allows access only to the uploader or institutional admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if hasattr(obj, 'uploaded_by') and obj.uploaded_by == request.user:
            return True

        if hasattr(obj, 'institution') and getattr(request.user, 'institution', None):
            return obj.institution == request.user.institution and getattr(request.user, 'is_admin', False)

        return False


class IsInstitutionAdmin(permissions.BasePermission):
    """
    Allows access only to institutional admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_admin', False)


class CanViewSharedFile(permissions.BasePermission):
    """
    Allows view if file is public, shared with user or role, or uploaded by the user.
    """
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True

        if obj.uploaded_by == request.user:
            return True

        # Check for explicit shared access
        shared = SharedAccess.objects.filter(file=obj)

        if shared.filter(user=request.user).exists():
            return True

        if getattr(request.user, 'role', None):
            if shared.filter(role=request.user.role).exists():
                return True

        if getattr(request.user, 'class_level', None):
            if shared.filter(class_level=request.user.class_level).exists():
                return True

        if getattr(request.user, 'stream', None):
            if shared.filter(stream=request.user.stream).exists():
                return True

        return False


class IsTeacherOrUploader(permissions.BasePermission):
    """
    Allow teacher or file uploader to access the object.
    """
    def has_object_permission(self, request, view, obj):
        return (
            getattr(request.user, 'is_teacher', False) or
            (hasattr(obj, 'uploaded_by') and obj.uploaded_by == request.user)
        )
