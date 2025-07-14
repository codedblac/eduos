import django_filters
from django.db.models import Q
from django.utils import timezone

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


class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Role
        fields = ['name', 'institution', 'is_active']


class PermissionFilter(django_filters.FilterSet):
    codename = django_filters.CharFilter(lookup_expr='icontains')
    module = django_filters.CharFilter(lookup_expr='icontains')
    is_global = django_filters.BooleanFilter()

    class Meta:
        model = Permission
        fields = ['codename', 'module', 'is_global']


class UserRoleAssignmentFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    role = django_filters.ModelChoiceFilter(queryset=Role.objects.all())
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    is_active = django_filters.BooleanFilter()
    assigned_at = django_filters.DateFromToRangeFilter()
    expires_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = UserRoleAssignment
        fields = ['user', 'role', 'institution', 'is_active', 'assigned_at', 'expires_at']


class RolePermissionFilter(django_filters.FilterSet):
    role = django_filters.ModelChoiceFilter(queryset=Role.objects.all())
    permission = django_filters.ModelChoiceFilter(queryset=Permission.objects.all())
    allow = django_filters.BooleanFilter()

    class Meta:
        model = RolePermission
        fields = ['role', 'permission', 'allow']


class RoleAuditLogFilter(django_filters.FilterSet):
    actor = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    target_user = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    role = django_filters.ModelChoiceFilter(queryset=Role.objects.all())
    action = django_filters.ChoiceFilter(choices=[
        ('assign', 'Assigned'),
        ('remove', 'Removed'),
        ('update', 'Updated'),
        ('create', 'Created'),
        ('deactivate', 'Deactivated'),
    ])
    timestamp = django_filters.DateFromToRangeFilter()

    class Meta:
        model = RoleAuditLog
        fields = ['actor', 'target_user', 'institution', 'role', 'action', 'timestamp']


class PermissionAuditLogFilter(django_filters.FilterSet):
    actor = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    permission = django_filters.ModelChoiceFilter(queryset=Permission.objects.all())
    target_role = django_filters.ModelChoiceFilter(queryset=Role.objects.all())
    action = django_filters.ChoiceFilter(choices=[
        ('add', 'Added'),
        ('remove', 'Removed'),
    ])
    timestamp = django_filters.DateFromToRangeFilter()

    class Meta:
        model = PermissionAuditLog
        fields = ['actor', 'permission', 'target_role', 'action', 'timestamp']
