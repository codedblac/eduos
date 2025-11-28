import django_filters
from institutions.models import Institution, SchoolAccount
from django_filters import rest_framework as filters


# =============================
# 🏫 Institution Filters
# =============================
class InstitutionFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='iexact')
    school_type = filters.CharFilter(field_name='school_type', lookup_expr='iexact')
    institution_type = filters.CharFilter(field_name='institution_type', lookup_expr='iexact')
    ownership = filters.CharFilter(field_name='ownership', lookup_expr='icontains')
    funding_source = filters.CharFilter(field_name='funding_source', lookup_expr='icontains')

    # Hierarchical location filters
    country = filters.CharFilter(field_name='country', lookup_expr='iexact')
    county = filters.CharFilter(field_name='county', lookup_expr='iexact')
    sub_county = filters.CharFilter(field_name='sub_county', lookup_expr='iexact')
    ward = filters.CharFilter(field_name='ward', lookup_expr='iexact')
    village = filters.CharFilter(field_name='village', lookup_expr='iexact')

    class Meta:
        model = Institution
        fields = [
            'name', 'code', 'school_type', 'institution_type', 'ownership', 'funding_source',
            'country', 'county', 'sub_county', 'ward', 'village',
        ]


# =============================
# 💳 School Account Filters
# =============================
class SchoolAccountFilter(filters.FilterSet):
    institution_name = filters.CharFilter(field_name='institution__name', lookup_expr='icontains')
    account_name = filters.CharFilter(field_name='account_name', lookup_expr='icontains')
    payment_type = filters.CharFilter(field_name='payment_type', lookup_expr='iexact')
    is_default = filters.BooleanFilter(field_name='is_default')

    class Meta:
        model = SchoolAccount
        fields = ['institution_name', 'account_name', 'payment_type', 'is_default']
