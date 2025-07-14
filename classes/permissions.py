from rest_framework import permissions


class IsInstitutionAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to institution staff or superusers for write operations.
    Read operations are open to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsReadOnlyOrInstitutionStaff(permissions.BasePermission):
    """
    Safe methods (GET, HEAD, OPTIONS) are allowed for all authenticated users.
    Write methods (POST, PUT, PATCH, DELETE) require staff/superuser.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsClassInstitutionMatch(permissions.BasePermission):
    """
    Object-level permission to ensure access is granted only if:
    - The user is a superuser, or
    - The object (ClassLevel or Stream) belongs to the same institution as the user.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        user_institution = getattr(request.user, 'institution', None)

        # Determine object's institution for both ClassLevel and Stream
        obj_institution = getattr(obj, 'institution', None)
        if obj_institution is None and hasattr(obj, 'class_level'):
            obj_institution = getattr(obj.class_level, 'institution', None)

        if not obj_institution:
            return False

        if request.method in permissions.SAFE_METHODS:
            return user_institution == obj_institution

        return (
            user_institution and obj_institution and user_institution == obj_institution and
            (request.user.is_staff or request.user.is_superuser)
        )
