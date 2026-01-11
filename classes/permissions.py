from rest_framework import permissions


# ======================================================
# 🏫 Institution Admin / Staff
# ======================================================

class IsInstitutionAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to institution admins, staff, or superusers.
    Used mainly for analytics, reports, AI, and sensitive operations.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return bool(
            request.user.is_superuser or
            request.user.is_staff
        )


# ======================================================
# 📖 Read-only for Authenticated, Write for Staff
# ======================================================

class IsReadOnlyOrInstitutionStaff(permissions.BasePermission):
    """
    - SAFE METHODS: Any authenticated user (admins, teachers)
    - WRITE METHODS: Institution staff or superusers only
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(
            request.user.is_superuser or
            request.user.is_staff
        )


# ======================================================
# 🔐 Object-Level Institution Guard
# ======================================================

class IsClassInstitutionMatch(permissions.BasePermission):
    """
    Object-level permission:
    - Superuser: full access
    - Institution staff: full access within institution
    - Teachers: read-only access to objects in their institution
    - Others: denied
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superuser bypass
        if request.user.is_superuser:
            return True

        user_institution = getattr(request.user, 'institution', None)
        if not user_institution:
            return False

        # --------------------------------------------------
        # Resolve object's institution
        # --------------------------------------------------
        obj_institution = getattr(obj, 'institution', None)

        # Stream → ClassLevel → Institution
        if obj_institution is None and hasattr(obj, 'class_level'):
            obj_institution = getattr(obj.class_level, 'institution', None)

        if not obj_institution:
            return False

        # Institution mismatch
        if user_institution != obj_institution:
            return False

        # --------------------------------------------------
        # SAFE METHODS (READ)
        # --------------------------------------------------
        if request.method in permissions.SAFE_METHODS:
            return True

        # --------------------------------------------------
        # WRITE METHODS
        # --------------------------------------------------
        return bool(
            request.user.is_staff
        )
