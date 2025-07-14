import django_filters
from institutions.models import Institution, SchoolAccount


class InstitutionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='iexact')
    school_type = django_filters.CharFilter(lookup_expr='iexact')
    ownership = django_filters.CharFilter(lookup_expr='icontains')
    funding_source = django_filters.CharFilter(lookup_expr='icontains')

    # Hierarchical location filters
    country = django_filters.CharFilter(lookup_expr='iexact')
    county = django_filters.CharFilter(lookup_expr='iexact')
    sub_county = django_filters.CharFilter(lookup_expr='iexact')
    ward = django_filters.CharFilter(lookup_expr='iexact')
    village = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Institution
        fields = [
            'name', 'code', 'school_type', 'ownership', 'funding_source',
            'country', 'county', 'sub_county', 'ward', 'village',
        ]


class SchoolAccountFilter(django_filters.FilterSet):
    institution__name = django_filters.CharFilter(lookup_expr='icontains')
    account_name = django_filters.CharFilter(lookup_expr='icontains')
    payment_type = django_filters.CharFilter(lookup_expr='iexact')
    is_default = django_filters.BooleanFilter()

    class Meta:
        model = SchoolAccount
        fields = ['institution__name', 'account_name', 'payment_type', 'is_default']
