from rest_framework import permissions


class IsGuardianOrReadOnly(permissions.BasePermission):
    """
    Allow full access to guardian on their own records,
    read-only to others (e.g., teachers, admins).
    """

    def has_object_permission(self, request, view, obj):
        # SAFE methods: GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the guardian can edit their own profile/records
        return hasattr(request.user, "guardian") and obj == request.user.guardian


class IsGuardianOwnerOfLink(permissions.BasePermission):
    """
    Only allow guardian to view/manage their own student links.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.guardian.user == request.user
        return hasattr(request.user, "guardian") and obj.guardian.user == request.user


class IsGuardianNotificationRecipient(permissions.BasePermission):
    """
    Guardian can only see their own notifications.
    """

    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, "guardian") and obj.guardian.user == request.user
