from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Admins of the institution can create/update/delete. Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated
            and user.is_staff
            and hasattr(user, 'institution')
        )


class IsSubjectOwnerOrInstitutionAdmin(permissions.BasePermission):
    """
    Only subject heads or institution admins can modify a subject.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.teacher_links.filter(teacher__user=user, is_head=True).exists()


class IsSubjectHeadOrTeacher(permissions.BasePermission):
    """
    Allow write if user is a subject head or assigned teacher. Others get read-only.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.teacher_links.filter(teacher__user=user).exists()


class IsSubjectTeacherOrReadOnly(permissions.BasePermission):
    """
    Allow write access to teachers assigned to the subject; others have read-only access.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.teacher_links.filter(teacher__user=user).exists()


class IsTeacherInInstitution(permissions.BasePermission):
    """
    Ensure user is a teacher in the institution (for nested/related views).
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, 'teacher_profile')
            and hasattr(user, 'institution')
        )


class IsHODOrAdminOrReadOnly(permissions.BasePermission):
    """
    Allow modification only if the user is an admin or Head of Department (subject head).
    Read-only for everyone else.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.teacher_links.filter(teacher__user=user, is_head=True).exists()
