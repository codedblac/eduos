from rest_framework import permissions


class IsGuardianOrReadOnly(permissions.BasePermission):
    """
    Allows full access to the guardian who owns the profile, else read-only access.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return hasattr(request.user, 'guardian_profile') and obj.user == request.user


class IsGuardianOfStudent(permissions.BasePermission):
    """
    Allows access only if the authenticated guardian is linked to the student.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, 'guardian_profile')

    def has_object_permission(self, request, view, obj):
        guardian = getattr(request.user, 'guardian_profile', None)
        return guardian and obj.guardian == guardian


class IsInstitutionAdminOrStaff(permissions.BasePermission):
    """
    Allow access only to users with admin/staff roles in the same institution.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role in ['admin', 'super_admin', 'staff']
        )


class CanViewGuardianNotifications(permissions.BasePermission):
    """
    Allow guardians to view their own notifications.
    Allow institution staff to view all guardian notifications.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        # Guardian can view own
        if hasattr(user, 'guardian_profile') and obj.guardian.user == user:
            return True

        # Staff/admin of same institution
        if hasattr(user, 'profile'):
            return obj.institution == user.profile.institution and user.profile.role in ['admin', 'super_admin', 'staff']

        return False
