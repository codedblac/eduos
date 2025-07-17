from rest_framework import permissions
from accounts.models import CustomUser


class IsInstitutionMember(permissions.BasePermission):
    """
    Allows access only to users belonging to the same institution.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, 'institution'):
            return obj.institution == user.institution
        elif hasattr(obj, 'event'):
            return obj.event.institution == user.institution
        return False


class IsEventCreatorOrReadOnly(permissions.BasePermission):
    """
    Allow full access only to the event creator; others get read-only.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'created_by', None) == request.user


class IsSelfForRSVPAndFeedback(permissions.BasePermission):
    """
    Only the authenticated user can manage their RSVP or feedback.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', None) == request.user


class CanManageEvent(permissions.BasePermission):
    """
    Allow editing only if user is event creator or institution admin.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.created_by == user or user.role == CustomUser.Role.ADMIN


class IsInstitutionAdmin(permissions.BasePermission):
    """
    Checks if the user is an admin in the current institution.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == CustomUser.Role.ADMIN
