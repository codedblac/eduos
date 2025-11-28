from rest_framework import permissions
from django.utils import timezone

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Allow instructors to edit, others can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'instructorprofile') and obj.created_by == request.user


class IsCourseOwnerOrAdmin(permissions.BasePermission):
    """
    Only the creator or an admin can edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.created_by == request.user


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Allow students to submit/participate, others read-only.
    """
    def has_permission(self, request, view):
        return request.user.primary_role== 'student' or request.method in permissions.SAFE_METHODS


class IsEnrolledStudent(permissions.BasePermission):
    """
    Only allow access if user is enrolled in the course.
    """
    def has_object_permission(self, request, view, obj):
        return obj.enrollments.filter(student__user=request.user).exists()


class IsThreadParticipant(permissions.BasePermission):
    """
    Only thread participants can access or reply.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class IsLessonStudentOrInstructor(permissions.BasePermission):
    """
    Restrict lesson-related progress or comments to enrolled students or instructors.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(user, 'student'):
            return obj.course.enrollments.filter(student=user.student).exists()
        if hasattr(user, 'instructorprofile'):
            return obj.course.created_by == user
        return False


class CanSubmitAssignment(permissions.BasePermission):
    """
    Students can only submit assignments before due date and if enrolled.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(user, 'student'):
            return obj.due_date >= timezone.now() and obj.course.enrollments.filter(student=user.student).exists()
        return False
