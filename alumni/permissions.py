from rest_framework import permissions


class IsInstitutionAdminOrReadOnly(permissions.BasePermission):
    """
    Allow only institution admins to modify; others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'institution') and request.user.role in ['admin', 'superadmin']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.institution == request.user.institution
        return hasattr(request.user, 'institution') and obj.institution == request.user.institution and request.user.role in ['admin', 'superadmin']


class IsAlumniOrReadOnly(permissions.BasePermission):
    """
    Alumni users can edit their own profile; others can view.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsMentorshipOwnerOrAdmin(permissions.BasePermission):
    """
    Only the mentor/mentee or admin can modify the mentorship record.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.mentor == request.user or obj.mentee == request.user or request.user.role in ['admin', 'superadmin']


class IsFeedbackOwnerOrReadOnly(permissions.BasePermission):
    """
    Alumni can update/delete their feedback. Others can view.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.submitted_by == request.user or request.user.role in ['admin', 'superadmin']
