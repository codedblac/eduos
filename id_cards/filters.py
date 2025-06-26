import django_filters
from .models import IDCard
from django.db.models import Q


class IDCardFilter(django_filters.FilterSet):
    institution = django_filters.NumberFilter(field_name='user__institution__id', lookup_expr='exact')
    role = django_filters.CharFilter(field_name='user__role', lookup_expr='iexact')
    status = django_filters.ChoiceFilter(field_name='status', choices=IDCard.STATUS_CHOICES)
    issued_after = django_filters.DateFilter(field_name='issued_on', lookup_expr='gte')
    issued_before = django_filters.DateFilter(field_name='issued_on', lookup_expr='lte')
    expires_after = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expires_before = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    is_digital = django_filters.BooleanFilter(field_name='is_digital')

    class Meta:
        model = IDCard
        fields = [
            'institution',
            'role',
            'status',
            'issued_after',
            'issued_before',
            'expires_after',
            'expires_before',
            'is_digital',
        ]
