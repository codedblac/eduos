# exams/permissions.py

from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'teacher'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsStudent(permissions.BasePermission):
    """
    Allow access only to authenticated users with role 'student'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Allow access to school admins and super admins only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class CanEnterMarks(permissions.BasePermission):
    """
    Allow only the teacher assigned to that ExamSubject to enter marks.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return False
        return obj.exam_subject.teacher.user == request.user


class CanGenerateAIInsights(permissions.BasePermission):
    """
    Allow only super admins to trigger AI insights or exam generation.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class CanViewOwnResults(permissions.BasePermission):
    """
    Students can only view their own scores.
    """
    def has_object_permission(self, request, view, obj):
        return obj.student.user == request.user
