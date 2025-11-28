# accounts/filters.py

import django_filters
from django.db.models import Q
from accounts.models import CustomUser


class UserFilter(django_filters.FilterSet):
    """
    Enhanced filter with:
    - Role (case insensitive)
    - Institution restriction
    - Name/email partial match
    - Active status
    - Date filters
    - Ordering by email or name
    """

    primary_role = django_filters.CharFilter(
        field_name='primary_role__name',
        lookup_expr='iexact',
        help_text="Filter by user primary role (case insensitive)"
    )

    institution = django_filters.NumberFilter(
        field_name='institution_id',
        help_text="Institution ID (Admins restricted automatically)"
    )

    is_active = django_filters.BooleanFilter()

    email = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Case-insensitive partial email match"
    )

    name = django_filters.CharFilter(
        method='filter_by_name',
        help_text="Partial match in first or last name (case-insensitive)"
    )

    date_joined_after = django_filters.DateTimeFilter(
        field_name='date_joined',
        lookup_expr='gte'
    )

    date_joined_before = django_filters.DateTimeFilter(
        field_name='date_joined',
        lookup_expr='lte'
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ("first_name", "first_name"),
            ("last_name", "last_name"),
            ("email", "email"),
        ),
        field_labels={
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
        },
        label="Order by"
    )

    class Meta:
        model = CustomUser
        # Only include real model fields or properly mapped filters here
        fields = [
            'primary_role', 'institution', 'is_active', 'email'
        ]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )
