from rest_framework import permissions
from .models import UserRoleAssignment, RolePermission, Permission, UserPermissionOverride
from institutions.models import Institution


class IsInstitutionMember(permissions.BasePermission):
    """
    Allows access only to users who have a role in the current institution context.
    """

    def has_permission(self, request, view):
        institution = getattr(request.user.profile, 'current_institution', None)
        return institution and UserRoleAssignment.objects.filter(
            user=request.user, institution=institution, is_active=True
        ).exists()


class HasInstitutionPermission(permissions.BasePermission):
    """
    Checks if the user has a specific permission (codename) in their current institution.
    Requires view.required_permission to be set.
    """

    def has_permission(self, request, view):
        institution = getattr(request.user.profile, 'current_institution', None)
        required_permission = getattr(view, 'required_permission', None)

        if not institution or not required_permission:
            return False

        # Check for direct override
        if UserPermissionOverride.objects.filter(
            user=request.user,
            permission__codename=required_permission,
            institution=institution,
            allow=True
        ).exists():
            return True

        # Check role-based permissions
        role_ids = UserRoleAssignment.objects.filter(
            user=request.user,
            institution=institution,
            is_active=True
        ).values_list('role', flat=True)

        return RolePermission.objects.filter(
            role_id__in=role_ids,
            permission__codename=required_permission,
            allow=True
        ).exists()


class HasAnyInstitutionPermission(permissions.BasePermission):
    """
    Allows access if the user has any one of the listed permissions (defined via view.allowed_permissions).
    """

    def has_permission(self, request, view):
        institution = getattr(request.user.profile, 'current_institution', None)
        allowed_permissions = getattr(view, 'allowed_permissions', [])

        if not institution or not allowed_permissions:
            return False

        # Direct override
        if UserPermissionOverride.objects.filter(
            user=request.user,
            permission__codename__in=allowed_permissions,
            institution=institution,
            allow=True
        ).exists():
            return True

        # Role permissions
        role_ids = UserRoleAssignment.objects.filter(
            user=request.user,
            institution=institution,
            is_active=True
        ).values_list('role', flat=True)

        return RolePermission.objects.filter(
            role_id__in=role_ids,
            permission__codename__in=allowed_permissions,
            allow=True
        ).exists()


class IsSuperAdmin(permissions.BasePermission):
    """
    Global superusers bypass all institutional role checks.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsRoleHolder(permissions.BasePermission):
    """
    Grants access only if user holds one of the specified roles (defined as `allowed_roles = ['Admin', 'Finance']`).
    """

    def has_permission(self, request, view):
        allowed_roles = getattr(view, 'allowed_roles', [])
        institution = getattr(request.user.profile, 'current_institution', None)

        if not institution or not allowed_roles:
            return False

        return UserRoleAssignment.objects.filter(
            user=request.user,
            institution=institution,
            role__name__in=allowed_roles,
            is_active=True
        ).exists()
