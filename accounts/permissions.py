from rest_framework import permissions


# ==============================
# Generic Role-Based Permission
# ==============================
class HasRole(permissions.BasePermission):
    """
    Allows access only to users with specific roles.
    Usage: permission_classes = [HasRole(User.Role.TEACHER, User.Role.PARENT)]
    """
    def __init__(self, *roles):
        self.roles = roles

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.roles
        )


# ==============================
# Super Admin
# ==============================
class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_super_admin
        )


# ==============================
# School Admin
# ==============================
class IsSchoolAdmin(permissions.BasePermission):
    """
    Allows access only to School Admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_school_admin
        )


# ==============================
# Institution Check
# ==============================
class IsSameInstitution(permissions.BasePermission):
    """
    Allows access only if the user's institution matches the object's institution.
    Assumes the object or its related user has an 'institution' attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin:
            return True

        user_institution = getattr(request.user, 'institution', None)
        obj_institution = getattr(obj, 'institution', None)

        # Check nested relationship if direct institution not found
        if obj_institution is None and hasattr(obj, 'user'):
            obj_institution = getattr(getattr(obj, 'user', None), 'institution', None)

        return user_institution and obj_institution and user_institution == obj_institution


# ==============================
# Ownership / Self Access
# ==============================
class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Allows users to edit their own information; read-only access otherwise.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


# ==============================
# Active Authenticated Users Only
# ==============================
class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Allows access only to authenticated and active users.
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )


# ==============================
# User Management Permissions
# ==============================
class CanManageUsers(permissions.BasePermission):
    """
    Allows School Admins and Super Admins to manage users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_super_admin:
            return True
        if request.user.is_school_admin:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin:
            return True
        return (
            request.user.is_school_admin and
            hasattr(obj, 'institution') and
            obj.institution == request.user.institution
        )


# ==============================
# Super Admin or Read Only
# ==============================
class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access for all authenticated users,
    but write access only to Super Admins.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_super_admin
        )
