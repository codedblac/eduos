# admissions/permissions.py

from rest_framework import permissions


class IsAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to admin or staff users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the object has a `user` or `applicant.user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'applicant') and hasattr(obj.applicant, 'user'):
            return obj.applicant.user == request.user
        return False


class IsApplicantOrReadOnly(permissions.BasePermission):
    """
    Allows applicants to view and edit their own applications,
    restricts others unless admin/staff.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return hasattr(obj, 'user') and obj.user == request.user


class CanManageAdmission(permissions.BasePermission):
    """
    For views like shortlisting, offers, entrance exams – restrict to staff/admin only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )


class CanViewOwnApplication(permissions.BasePermission):
    """
    Allows applicant to view only their own admission data.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'applicant') and hasattr(obj.applicant, 'user'):
            return obj.applicant.user == request.user
        return False
