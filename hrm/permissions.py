from rest_framework import permissions


class IsHRManager(permissions.BasePermission):
    """
    Allows access only to users with 'hr_manager' role or superuser.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            getattr(request.user, 'role', None) == 'hr_manager' or request.user.is_superuser
        )


class IsDepartmentHead(permissions.BasePermission):
    """
    Allows department heads to manage staff within their own department.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'hr_manager' or user.is_superuser:
            return True

        # Ensure the user has an associated StaffHRRecord
        try:
            staff_record = user.staffhrrecord
        except AttributeError:
            return False

        return obj.department == staff_record.department


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Allow users to read their own profile; only HR can modify.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or request.user.role == 'hr_manager'
        return request.user.role == 'hr_manager' or request.user.is_superuser


class IsAdminOrHR(permissions.BasePermission):
    """
    Grants access to superusers and HR managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'hr_manager'
        )
