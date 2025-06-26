import django_filters
from .models import Subject


class SubjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.NumberFilter(field_name='institution__id')

    class Meta:
        model = Subject
        fields = ['name', 'institution']
