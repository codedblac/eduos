from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access to institution admins, read-only to others.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and getattr(request.user, 'is_institution_admin', False)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.institution == getattr(request.user, 'institution', None)
        return (
            request.user.is_authenticated and
            getattr(request.user, 'is_institution_admin', False) and
            obj.institution == getattr(request.user, 'institution', None)
        )


class IsTeacherOrInstitutionAdmin(permissions.BasePermission):
    """
    Allow access if the user is the teacher themselves or the institution admin.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, 'teacher_profile') and obj == request.user.teacher_profile:
            return True

        if getattr(request.user, 'is_institution_admin', False) and obj.institution == request.user.institution:
            return True

        return False


class IsTeacherUserOrReadOnly(permissions.BasePermission):
    """
    Authenticated teachers can access their own profile. Admins can modify others.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        if hasattr(request.user, 'teacher_profile') and obj == request.user.teacher_profile:
            return True

        return getattr(request.user, 'is_institution_admin', False)
