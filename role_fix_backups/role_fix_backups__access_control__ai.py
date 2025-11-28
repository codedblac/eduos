from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

from access_control.models import (
    Role,
    Permission,
    UserRoleAssignment,
    RolePermission,
    UserPermissionOverride,
)
from accounts.models import CustomUser
from institutions.models import Institution


class AccessControlAIEngine:
    """
    AI engine to enhance and analyze access control logic.
    """

    @staticmethod
    def recommend_roles_for_user(user: CustomUser):
        """
        Suggest possible roles for a user based on metadata or naming patterns.
        Example: Superuser → super_admin, email → teacher, profile.job_title → principal/bursar
        """
        keywords_to_roles = {
            'teacher': 'Teacher',
            'bursar': 'Finance',
            'principal': 'Principal',
            'admin': 'Administrator',
        }

        matched_roles = set()

        if user.is_superuser:
            matched_roles.add('Super Admin')

        if user.email:
            for keyword, role_name in keywords_to_roles.items():
                if keyword in user.email.lower():
                    matched_roles.add(role_name)

        if hasattr(user, 'profile') and user.profile.job_title:
            job_title = user.profile.job_title.lower()
            for keyword, role_name in keywords_to_roles.items():
                if keyword in job_title:
                    matched_roles.add(role_name)

        return Role.objects.filter(name__in=matched_roles)

    @staticmethod
    def detect_unused_roles(institution: Institution, days: int = 90):
        """
        Detect institution roles that have not been assigned to any user in the last N days.
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        return Role.objects.filter(
            institution=institution,
            user_assignments__isnull=True,
            created_at__lt=cutoff_date,
            is_active=True
        )

    @staticmethod
    def detect_permission_anomalies(institution: Institution, threshold: int = 5):
        """
        Identify users whose actual permission counts differ from the expected count significantly.
        This can indicate misconfigured roles or overrides.
        """
        anomalies = []

        role_permission_map = RolePermission.objects.filter(
            role__institution=institution
        ).values('role_id').annotate(total=Count('permission'))

        expected_permission_count = {
            entry['role_id']: entry['total'] for entry in role_permission_map
        }

        assignments = UserRoleAssignment.objects.filter(
            institution=institution,
            is_active=True
        ).select_related('role', 'user')

        for assignment in assignments:
            role_id = assignment.primary_role.id
            expected = expected_permission_count.get(role_id, 0)

            actual_permissions = Permission.objects.filter(
                rolepermission__role=assignment.primary_role
            ).distinct().count()

            # You could also count custom overrides if needed
            # actual_overrides = UserPermissionOverride.objects.filter(
            #     user=assignment.user,
            #     institution=institution
            # ).count()

            if abs(expected - actual_permissions) >= threshold:
                anomalies.append({
                    "user": assignment.user,
                    "role": assignment.primary_role,
                    "expected_permissions": expected,
                    "actual_permissions": actual_permissions,
                })

        return anomalies

    @staticmethod
    def suggest_permissions_for_role(role: Role, institution: Institution = None):
        """
        Suggest permissions for a new role based on similar role names across the institution or globally.
        """
        if not institution:
            institution = role.institution

        similar_roles = Role.objects.filter(
            Q(name__icontains=role.name) |
            Q(description__icontains=role.name),
            institution=institution
        ).exclude(id=role.id)

        permissions = Permission.objects.filter(
            rolepermission__role__in=similar_roles
        ).distinct()

        return permissions
