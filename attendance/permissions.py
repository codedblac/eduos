from rest_framework import permissions
from accounts.models import CustomUser


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsAttendanceAdmin(permissions.BasePermission):
    """
    Allow only users with an admin/attendance role or superusers to manage attendance records.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['ADMIN', 'ATTENDANCE_ADMIN', 'HR'] or request.user.is_superuser
        )


class IsTeacherOrStaff(permissions.BasePermission):
    """
    Allow teachers or staff to view and manage their own attendance data.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['TEACHER', 'STAFF', 'SUPPORT_STAFF']


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Users can view their own attendance logs. Admins can view others.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.user == request.user or request.user.is_superuser
        return request.user.role in ['ADMIN', 'ATTENDANCE_ADMIN'] or request.user.is_superuser


class IsRecordedBySelfOrAdmin(permissions.BasePermission):
    """
    Only the recorder or an admin can modify attendance entries.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.recorded_by == request.user or request.user.role in ['ADMIN', 'ATTENDANCE_ADMIN']


class IsInstitutionMatch(permissions.BasePermission):
    """
    Ensures a user can only manage attendance within their own institution.
    """
    def has_object_permission(self, request, view, obj):
        return obj.institution == request.user.institution


class CanViewSummaries(permissions.BasePermission):
    """
    Allow summary viewing by admins, HR, and attendance officers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'ADMIN', 'HR', 'ATTENDANCE_ADMIN', 'AUDITOR'
        ]
