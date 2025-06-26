from rest_framework import permissions


class CanManageSubjects(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'superadmin']
