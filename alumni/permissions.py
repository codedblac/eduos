# alumni/permissions.py

from rest_framework import permissions

class IsInstitutionStaffOrAdmin(permissions.BasePermission):
    """
    Grants full access to institution staff or admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.primary_role in ['admin', 'staff', 'super_admin'] and request.user.institution is not None

    def has_object_permission(self, request, view, obj):
        return obj.institution == request.user.institution


class IsAlumniOwnerOrReadOnly(permissions.BasePermission):
    """
    Alumni users can view and update their own profiles or feedback.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student') and hasattr(request.user.student, 'alumni_profile')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.alumni.student == request.user.student
        return obj.alumni.student == request.user.student


class IsAlumniSelf(permissions.BasePermission):
    """
    Only the alumni user associated with the profile can access or modify.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student') and hasattr(request.user.student, 'alumni_profile')

    def has_object_permission(self, request, view, obj):
        return obj.student == request.user.student


class IsMentorshipParticipant(permissions.BasePermission):
    """
    Allows access only if the user is the mentor or the student in the mentorship.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'student') and obj.mentee == request.user.student:
            return True
        if hasattr(request.user, 'student') and hasattr(request.user.student, 'alumni_profile'):
            return obj.mentor == request.user.student.alumni_profile
        return False


class IsEventRegistrantOrAdmin(permissions.BasePermission):
    """
    Alumni can view their own event registrations. Staff/admin can manage all.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.primary_role in ['admin', 'staff', 'super_admin']:
            return obj.event.institution == request.user.institution
        if hasattr(request.user, 'student') and hasattr(request.user.student, 'alumni_profile'):
            return obj.alumni == request.user.student.alumni_profile
        return False
