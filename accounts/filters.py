# accounts/filters.py

import django_filters
from django.db.models import Q
from accounts.models import CustomUser


class UserFilter(django_filters.FilterSet):
    """
    Filter and search users by:
    - role
    - institution
    - email (partial match)
    - full name (first/last, partial match)
    - is_active
    - date_joined range
    """

    role = django_filters.CharFilter(
        field_name='role',
        lookup_expr='iexact',
        help_text="Filter by user role (e.g., TEACHER, ADMIN, STUDENT)"
    )

    institution = django_filters.NumberFilter(
        field_name='institution_id',
        help_text="Institution ID"
    )

    is_active = django_filters.BooleanFilter(
        help_text="Active status"
    )

    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        help_text="Partial email match"
    )

    name = django_filters.CharFilter(
        method='filter_by_name',
        label='Search by Name',
        help_text="Partial match in first or last name"
    )

    date_joined_after = django_filters.DateTimeFilter(
        field_name='date_joined',
        lookup_expr='gte',
        label='Joined After',
        help_text="Filter users joined on or after this datetime"
    )

    date_joined_before = django_filters.DateTimeFilter(
        field_name='date_joined',
        lookup_expr='lte',
        label='Joined Before',
        help_text="Filter users joined on or before this datetime"
    )

    class Meta:
        model = CustomUser
        fields = [
            'role', 'institution', 'is_active',
            'email', 'name', 'date_joined_after', 'date_joined_before'
        ]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )
