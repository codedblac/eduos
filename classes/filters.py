# classes/filters.py

import django_filters
from .models import ClassLevel, Stream


class ClassLevelFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.NumberFilter(field_name='institution__id')

    class Meta:
        model = ClassLevel
        fields = ['name', 'code', 'institution']


class StreamFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    class_level = django_filters.NumberFilter(field_name='class_level__id')

    class Meta:
        model = Stream
        fields = ['name', 'code', 'class_level']
