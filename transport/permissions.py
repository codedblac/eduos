from rest_framework import permissions

class IsInstitutionTransportStaff(permissions.BasePermission):
    """
    Allow access only to transport staff, drivers, or school admins within their institution.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.institution is not None

    def has_object_permission(self, request, view, obj):
        return obj.institution == request.user.institution


class IsTransportAdminOrReadOnly(permissions.BasePermission):
    """
    Allow full access to transport admins or institutional staff.
    Others (students/guardians) get read-only.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'staff', 'transport', 'super_admin']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.institution == request.user.institution
        return request.user.role in ['admin', 'staff', 'transport', 'super_admin'] and obj.institution == request.user.institution


class IsGuardianOrStudentForTransportViewOnly(permissions.BasePermission):
    """
    Allow guardians and students to view their transport assignments/attendance only.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['student', 'guardian']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'student':
            return hasattr(request.user, 'student') and obj.student == request.user.student
        elif request.user.role == 'guardian':
            return obj.student.guardianstudentlink_set.filter(guardian=request.user.guardian).exists()
        return False
