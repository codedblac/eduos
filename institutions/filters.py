# institutions/filters.py

import django_filters
from .models import Institution, SchoolAccount


class InstitutionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    registration_number = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.CharFilter(lookup_expr='exact')
    ownership = django_filters.CharFilter(lookup_expr='exact')
    county = django_filters.CharFilter(lookup_expr='icontains')
    sub_county = django_filters.CharFilter(lookup_expr='icontains')
    ward = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.BooleanFilter()

    class Meta:
        model = Institution
        fields = [
            'name', 'registration_number', 'type', 'ownership',
            'county', 'sub_county', 'ward', 'status'
        ]


class SchoolAccountFilter(django_filters.FilterSet):
    account_name = django_filters.CharFilter(lookup_expr='icontains')
    account_number = django_filters.CharFilter(lookup_expr='icontains')
    bank_name = django_filters.CharFilter(lookup_expr='icontains')
    account_type = django_filters.CharFilter(lookup_expr='exact')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = SchoolAccount
        fields = [
            'account_name', 'account_number', 'bank_name',
            'account_type', 'is_active'
        ]
