from rest_framework import permissions

class IsInstitutionGuardian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'guardian' and hasattr(request.user, 'guardian')
