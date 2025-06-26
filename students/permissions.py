from rest_framework import permissions


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Allows access only to users with admin or superadmin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsAssignedClassTeacher(permissions.BasePermission):
    """
    Allows access only if the teacher is assigned to the student's class.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and user.role == 'teacher' and obj.assigned_class_teacher == user


class IsParentOfStudent(permissions.BasePermission):
    """
    Allows access if the user is the parent linked to the student.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and user.role == 'parent' and obj.parents.filter(id=user.id).exists()


class CanManageStudents(permissions.BasePermission):
    """
    Custom permission for any user who can manage student data.
    Admins and SuperAdmins can manage.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class CanViewStudentProfile(permissions.BasePermission):
    """
    Parents can view their own children's data,
    Teachers can view students in their stream/class,
    Admins can view all.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role in ['admin', 'superadmin']:
            return True
        if user.role == 'teacher':
            return obj.stream and obj.stream.teachers.filter(id=user.id).exists()
        if user.role == 'parent':
            return obj.parents.filter(id=user.id).exists()
        return False
