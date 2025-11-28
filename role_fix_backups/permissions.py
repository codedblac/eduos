from rest_framework import permissions


class IsInstitutionTransportStaff(permissions.BasePermission):
    """
    Grants access only to authenticated transport staff or institutional members.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'institution') and
            request.user.institution is not None
        )

    def has_object_permission(self, request, view, obj):
        return (
            hasattr(request.user, 'institution') and
            obj.institution == request.user.institution
        )


class IsTransportAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access to transport-related staff (admin, staff, transport roles).
    Other users (like students/guardians) have read-only access.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.primary_role in ['admin', 'staff', 'transport', 'super_admin']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (
                hasattr(request.user, 'institution') and
                obj.institution == request.user.institution
            )
        return (
            request.user.primary_role in ['admin', 'staff', 'transport', 'super_admin'] and
            hasattr(request.user, 'institution') and
            obj.institution == request.user.institution
        )


class IsGuardianOrStudentForTransportViewOnly(permissions.BasePermission):
    """
    Allow only authenticated students or guardians to view relevant records (assignments, notifications, etc.).
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.primary_role in ['student', 'guardian']
        )

    def has_object_permission(self, request, view, obj):
        if request.user.primary_role== 'student':
            return (
                hasattr(request.user, 'student') and
                obj.student == request.user.student
            )
        elif request.user.primary_role== 'guardian':
            return (
                hasattr(request.user, 'guardian') and
                obj.student.guardianstudentlink_set.filter(
                    guardian=request.user.guardian
                ).exists()
            )
        return False
