from rest_framework import permissions


class IsInstitutionAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to authenticated institution staff or superusers.
    Recommended for full CRUD access on students.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsReadOnlyOrInstitutionStaff(permissions.BasePermission):
    """
    Read-only for unauthenticated or non-staff users.
    Write access restricted to institution staff or superusers.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsStudentInstitutionMatch(permissions.BasePermission):
    """
    Ensures a user can only operate on student records from their own institution.
    Object-level check.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        user_institution = getattr(request.user, 'institution', None)
        student_institution = getattr(obj, 'institution', None)
        return (
            request.user.is_authenticated and
            user_institution and student_institution and
            user_institution == student_institution
        )


class IsGuardianOfStudent(permissions.BasePermission):
    """
    Allows access to guardians only if they are linked to the student.
    Intended for limited read-access (e.g. medical records, performance).
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        guardian_profile = getattr(request.user, 'guardian_profile', None)
        if not guardian_profile:
            return False

        return obj.linked_guardians.filter(guardian=guardian_profile).exists()


class IsTeacherOfStudent(permissions.BasePermission):
    """
    Grants access to a teacher if the student is in their class/stream.
    Useful for class teachers accessing assigned students.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        teacher_profile = getattr(request.user, 'teacher_profile', None)
        if not teacher_profile:
            return False

        return (
            obj.assigned_class_teacher == teacher_profile or
            obj.stream in teacher_profile.streams.all()
        )
