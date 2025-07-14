from rest_framework import permissions
from reports.models import ReportAccessLevel
import logging

logger = logging.getLogger(__name__)


def get_user_institution(user):
    """
    Safely returns the institution for a user based on their role.
    """
    try:
        if hasattr(user, 'institution'):
            return user.institution
        elif hasattr(user, 'teacher_profile'):
            return user.teacher_profile.institution
        elif hasattr(user, 'guardian_profile'):
            return user.guardian_profile.institution
        elif hasattr(user, 'student_profile'):
            return user.student_profile.institution
    except Exception as e:
        logger.warning(f"Could not determine institution for user {user.id}: {e}")
    return None


class IsReportCreatorOrAdmin(permissions.BasePermission):
    """
    Grants full access to the user who generated the report, an institution admin, or a superuser.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.generated_by or
            getattr(request.user, 'is_institution_admin', False) or
            request.user.is_superuser
        )


class CanViewReportByAccessLevel(permissions.BasePermission):
    """
    Controls report visibility based on the report's access_level field.
    """
    def has_object_permission(self, request, view, obj):
        access = obj.access_level
        user = request.user

        if access == ReportAccessLevel.ADMIN:
            return user.is_superuser or getattr(user, 'is_institution_admin', False)

        if access == ReportAccessLevel.TEACHER:
            return getattr(user, 'is_teacher', False) or user.is_superuser

        if access == ReportAccessLevel.GUARDIAN:
            return getattr(user, 'is_guardian', False) or user.is_superuser

        if access == ReportAccessLevel.STUDENT:
            return getattr(user, 'is_student', False) or user.is_superuser

        return False


class IsInstitutionMember(permissions.BasePermission):
    """
    Ensures the user belongs to the same institution as the report.
    """
    def has_object_permission(self, request, view, obj):
        user_institution = get_user_institution(request.user)
        return user_institution == obj.institution


class CanGenerateReports(permissions.BasePermission):
    """
    Grants report generation permissions to teachers, admins, and superusers.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or
            getattr(user, 'is_institution_admin', False) or
            getattr(user, 'is_teacher', False)
        )
