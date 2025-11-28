from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from access_control.models import (
    Role,
    Permission,
    UserRoleAssignment,
    RolePermission,
    RoleAuditLog,
    PermissionAuditLog,
)
from accounts.models import CustomUser
from institutions.models import Institution


class AccessControlAnalytics:
    """
    Analytics and insights engine for roles, permissions, and assignments in EduOS.
    """

    @staticmethod
    def total_roles(institution: Institution = None):
        qs = Role.objects.filter(is_active=True)
        if institution:
            qs = qs.filter(institution=institution)
        return qs.count()

    @staticmethod
    def total_permissions():
        return Permission.objects.count()

    @staticmethod
    def total_assignments(institution: Institution = None):
        qs = UserRoleAssignment.objects.filter(is_active=True)
        if institution:
            qs = qs.filter(institution=institution)
        return qs.count()

    @staticmethod
    def most_assigned_roles(institution: Institution = None, top_n: int = 5):
        qs = UserRoleAssignment.objects.filter(is_active=True).values(
            'role__name'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        if institution:
            qs = qs.filter(institution=institution)
        return qs[:top_n]

    @staticmethod
    def least_used_roles(institution: Institution = None, top_n: int = 5):
        qs = Role.objects.filter(is_active=True).annotate(
            assignments=Count('user_assignments')
        ).order_by('assignments')
        if institution:
            qs = qs.filter(institution=institution)
        return qs[:top_n]

    @staticmethod
    def users_with_multiple_roles(institution: Institution = None):
        qs = UserRoleAssignment.objects.filter(is_active=True).values('user').annotate(
            role_count=Count('primary_role')
        ).filter(role_count__gt=1)
        if institution:
            qs = qs.filter(institution=institution)
        return qs.count()

    @staticmethod
    def permission_usage_stats():
        """
        Count how many roles each permission is assigned to.
        """
        return RolePermission.objects.values(
            'permission__codename', 'permission__module'
        ).annotate(
            usage_count=Count('primary_role')
        ).order_by('-usage_count')

    @staticmethod
    def recent_audit_logs(days: int = 30, limit: int = 50):
        """
        Get recent role or permission changes for admins to review.
        """
        since = timezone.now() - timedelta(days=days)
        role_logs = RoleAuditLog.objects.filter(timestamp__gte=since).order_by('-timestamp')[:limit]
        permission_logs = PermissionAuditLog.objects.filter(timestamp__gte=since).order_by('-timestamp')[:limit]
        return {
            'role_logs': role_logs,
            'permission_logs': permission_logs
        }

    @staticmethod
    def unassigned_permissions():
        """
        Permissions not currently assigned to any role.
        """
        return Permission.objects.filter(rolepermission__isnull=True)

    @staticmethod
    def orphan_roles():
        """
        Roles that have no permissions and no user assignments.
        """
        return Role.objects.annotate(
            permission_count=Count('permissions'),
            user_count=Count('user_assignments')
        ).filter(
            permission_count=0,
            user_count=0,
            is_active=True
        )

    @staticmethod
    def permissions_by_module():
        """
        Summary of permissions grouped by module.
        """
        return Permission.objects.values('module').annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def role_distribution_by_institution():
        """
        Return total roles per institution for multi-tenant environments.
        """
        return Role.objects.filter(institution__isnull=False).values(
            'institution__name'
        ).annotate(total=Count('id')).order_by('-total')
