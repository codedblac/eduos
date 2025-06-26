# timetable/permissions.py

from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to superadmins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class CanManageTimetable(permissions.BasePermission):
    """
    Allows access to superadmins and school-level admins who manage timetables.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['superadmin', 'admin']
        )


class CanViewOwnTimetable(permissions.BasePermission):
    """
    Teachers can only view timetable entries assigned to them.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'teacher':
            return obj.teacher.user == request.user
        return False
