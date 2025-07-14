import django_filters
from .models import ClassLevel, Stream


class ClassLevelFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    institution_id = django_filters.NumberFilter(field_name='institution__id')
    is_graduating_level = django_filters.BooleanFilter()
    requires_national_exam = django_filters.BooleanFilter()
    order_min = django_filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = django_filters.NumberFilter(field_name='order', lookup_expr='lte')

    class Meta:
        model = ClassLevel
        fields = [
            'name', 'code', 'institution_id',
            'is_graduating_level', 'requires_national_exam',
            'order_min', 'order_max'
        ]


class StreamFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
    class_level_id = django_filters.NumberFilter(field_name='class_level__id')
    class_level_name = django_filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    institution_id = django_filters.NumberFilter(field_name='institution__id')
    academic_year_id = django_filters.NumberFilter(field_name='academic_year__id')
    is_active = django_filters.BooleanFilter()
    class_teacher_id = django_filters.NumberFilter(field_name='class_teacher__id')
    order_min = django_filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_max = django_filters.NumberFilter(field_name='order', lookup_expr='lte')

    class Meta:
        model = Stream
        fields = [
            'name', 'code', 'class_level_id', 'class_level_name',
            'institution_id', 'academic_year_id',
            'is_active', 'class_teacher_id',
            'order_min', 'order_max'
        ]
