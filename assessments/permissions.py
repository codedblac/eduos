from rest_framework import permissions
from .models import AssessmentLock, AssessmentSession, AssessmentVisibility


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission for teachers or admin/staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'is_teacher', False)
        )


class IsStudent(permissions.BasePermission):
    """
    Permission for students only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_student', False)


class CanSubmitAssessment(permissions.BasePermission):
    """
    Students can submit only if the assessment is not locked.
    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, AssessmentSession):
            return False
        try:
            lock = AssessmentLock.objects.get(assessment=obj.assessment)
            return not lock.locked
        except AssessmentLock.DoesNotExist:
            return True  # No lock, so submission is allowed


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
    Students can view feedback only if visibility is enabled.
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
    Students can view scores only if visibility is enabled.
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
    Allows access to the object if user is the owner (student) or a teacher/staff.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(request.user, 'is_teacher', False):
            return True
        return hasattr(obj, 'student') and obj.student.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Restricts access strictly to the student who owns the session or answer.
    """
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'student') and obj.student.user == request.user
