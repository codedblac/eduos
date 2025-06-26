from rest_framework import permissions


class IsInstitutionStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow institutional staff (e.g. front office, security) to edit objects.
    Read-only access is allowed for authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return request.user and request.user.is_authenticated and request.user.is_institution_staff()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a ticket/appointment/etc. to edit it.
    Useful for tickets submitted by guardians/visitors.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.submitted_by == request.user or obj.requested_by == request.user


class IsSecurityStaff(permissions.BasePermission):
    """
    Allows access only to users marked as security staff.
    You can define this via a role flag or group membership.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_security_staff()


class IsFrontDeskStaff(permissions.BasePermission):
    """
    Allows access only to front desk staff for certain operations.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_front_desk()
