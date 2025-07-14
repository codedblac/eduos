from rest_framework import permissions


class IsAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to authenticated users who are staff or superuser.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Works with objects having `user` or `applicant.user` attributes.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'applicant') and hasattr(obj.applicant, 'user'):
            return obj.applicant.user == request.user
        return request.method in permissions.SAFE_METHODS


class IsApplicantOrReadOnly(permissions.BasePermission):
    """
    Allows applicants to read or modify their own application data.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return request.method in permissions.SAFE_METHODS


class CanManageAdmission(permissions.BasePermission):
    """
    Staff/superusers can manage entrance exams, shortlisting, offers, and status changes.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class CanViewOwnApplication(permissions.BasePermission):
    """
    Restricts access to one's own application unless staff/admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'applicant') and hasattr(obj.applicant, 'user'):
            return obj.applicant.user == request.user
        return False


class IsInstitutionStaff(permissions.BasePermission):
    """
    Ensures user belongs to the same institution and is staff/admin.
    Useful in multi-tenant setups.
    """

    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'institution'):
            return False
        if hasattr(obj, 'institution'):
            return obj.institution == request.user.institution and (
                request.user.is_staff or request.user.is_superuser
            )
        if hasattr(obj, 'applicant') and hasattr(obj.applicant, 'admission_session'):
            return (
                obj.applicant.admission_session.institution == request.user.institution and
                (request.user.is_staff or request.user.is_superuser)
            )
        return False
