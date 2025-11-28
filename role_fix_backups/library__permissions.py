# library/permissions.py

from rest_framework import permissions
from accounts.models import CustomUser


class IsLibrarian(permissions.BasePermission):
    """
    Allow access only to users with the 'Librarian' role.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'primary_role') and request.user.primary_role== CustomUser.LIBRARIAN


class IsStudent(permissions.BasePermission):
    """
    Allow access only to students.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'primary_role') and request.user.primary_role== CustomUser.STUDENT


class IsTeacher(permissions.BasePermission):
    """
    Allow access only to teachers.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'primary_role') and request.user.primary_role== CustomUser.TEACHER


class IsAdminOrLibrarian(permissions.BasePermission):
    """
    Allow access to librarians or institution admins.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'primary_role') and request.user.primary_role in [
            CustomUser.ADMIN, CustomUser.LIBRARIAN
        ]


class IsSuperAdmin(permissions.BasePermission):
    """
    Grant access to platform super admins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsInstitutionMember(permissions.BasePermission):
    """
    Ensure user and object belong to the same institution.
    Requires the object to have an `institution` FK.
    """
    def has_object_permission(self, request, view, obj):
        user_inst = getattr(request.user, 'institution', None)
        obj_inst = getattr(obj, 'institution', None)
        return user_inst and obj_inst and user_inst == obj_inst


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow object owners to edit; read allowed to everyone.
    Object must have a `user` field.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'user', None) == request.user


class IsLibraryMember(permissions.BasePermission):
    """
    Allow access to active registered library members only.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'librarymember') and request.user.librarymember.is_active


class IsBookOwnerOrLibrarian(permissions.BasePermission):
    """
    Allow only librarians or the user who rated/reviewed/requested a book.
    For models like BookRating, BookRequest.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.primary_role== CustomUser.LIBRARIAN:
            return True
        return getattr(obj, 'user', None) == request.user


class CanManageBookCopies(permissions.BasePermission):
    """
    Restrict creation/updating of book copies to librarians or admins.
    """
    def has_permission(self, request, view):
        return request.user.primary_role in [CustomUser.ADMIN, CustomUser.LIBRARIAN]
