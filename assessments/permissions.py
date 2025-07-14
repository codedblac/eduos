from rest_framework import permissions
from .models import AssessmentLock, AssessmentSession, AssessmentVisibility


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Allow only teachers or staff/admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'is_teacher', False)
        )


class IsStudent(permissions.BasePermission):
    """
    Allow only students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_student', False)


class CanSubmitAssessment(permissions.BasePermission):
    """
    Student can only submit if the assessment is not locked.
    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, AssessmentSession):
            return False
        try:
            lock = AssessmentLock.objects.get(assessment=obj.assessment)
            return not lock.locked
        except AssessmentLock.DoesNotExist:
            return True


class CanGradeAssessment(permissions.BasePermission):
    """
    Only teachers/staff can grade, and assessment must not be locked.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if not (request.user.is_staff or getattr(request.user, 'is_teacher', False)):
            return False
        try:
            lock = AssessmentLock.objects.get(assessment=obj.assessment)
            return not lock.locked
        except AssessmentLock.DoesNotExist:
            return True


class CanViewFeedback(permissions.BasePermission):
    """
    Students can only view feedback if visibility is allowed.
    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, AssessmentSession):
            return False
        try:
            visibility = AssessmentVisibility.objects.get(session=obj)
            return visibility.can_view_feedback
        except AssessmentVisibility.DoesNotExist:
            return False


class CanViewScore(permissions.BasePermission):
    """
    Students can only view their score if visibility is allowed.
    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, AssessmentSession):
            return False
        try:
            visibility = AssessmentVisibility.objects.get(session=obj)
            return visibility.can_view_score
        except AssessmentVisibility.DoesNotExist:
            return False


class IsOwnerOrTeacher(permissions.BasePermission):
    """
    Object-level permission to only allow owners (students) or teachers to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(request.user, 'is_teacher', False):
            return True
        if hasattr(obj, 'student') and obj.student.user == request.user:
            return True
        return False
